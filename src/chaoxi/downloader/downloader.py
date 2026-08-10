from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path

import httpx
from pydantic import BaseModel
from rich.console import Console
from rich.progress import Progress, TaskID

from chaoxi.exceptions import (
    ApiError,
    FileSystemError,
    NetworkError,
    RateLimitError,
)
from chaoxi.http_client import CninfoClient
from chaoxi.models import Announcement
from chaoxi.utils.config import AppSettings

_ILLEGAL_CHARS_RE = re.compile(r'[/:*?"<>|]')


def safe_filename(title: str) -> str:
    return _ILLEGAL_CHARS_RE.sub("_", title)


class DownloadTracker(BaseModel):
    total: int = 0
    success: int = 0
    failed: int = 0
    skipped: int = 0
    total_bytes: int = 0


class PdfDownloader:
    def __init__(
        self,
        client: CninfoClient,
        settings: AppSettings,
        download_dir: str,
        output_dir: str,
        skip_confirm: bool,
        max_concurrent: int = 4,
    ):
        self._client = client
        self._settings = settings
        self._download_dir = download_dir
        self._output_dir = output_dir
        self._skip_confirm = skip_confirm
        self._max_concurrent = max_concurrent
        self._stop_event = asyncio.Event()

    async def download(
        self, announcements: list[Announcement]
    ) -> tuple[list[Announcement], DownloadTracker]:
        pending = [a for a in announcements if a.status is None]
        if not pending:
            tracker = DownloadTracker(total=len(announcements))
            return announcements, tracker

        estimated_mb = sum(a.adjunct_size for a in pending) / 1024.0
        if not await self._confirm(len(pending), estimated_mb):
            for a in pending:
                a.status = "skipped"
            tracker = self._build_tracker(announcements)
            return announcements, tracker

        Path(self._download_dir).mkdir(parents=True, exist_ok=True)
        Path(self._output_dir).mkdir(parents=True, exist_ok=True)

        results = await self._download_all(pending)

        original_order = {id(a): i for i, a in enumerate(announcements)}
        results.sort(key=lambda a: original_order.get(id(a), 9999))

        await self._write_failed(results)

        tracker = self._build_tracker(results)
        return results, tracker

    async def _confirm(self, total: int, estimated_size_mb: float) -> bool:
        threshold = self._settings.download_confirm_threshold
        if total <= threshold:
            return True
        if not sys.stdin.isatty():
            Console().print("[yellow]非交互终端，跳过下载确认。[/yellow]")
            return True
        if self._skip_confirm:
            return True
        prompt = f"即将下载 {total} 个 PDF（约 {estimated_size_mb:.1f} MB），是否继续？"
        if total > 50:
            prompt += "\n    建议：仅生成 JSON 文件，后续交由 AI 处理 PDF 下载与识别"
        prompt += "\n[y/N]: "
        answer = input(prompt)
        return answer.strip().lower() == "y"

    async def _download_all(
        self,
        announcements: list[Announcement],
    ) -> list[Announcement]:
        sem = asyncio.Semaphore(self._max_concurrent)

        async def _download_one(ann: Announcement) -> Announcement:
            async with sem:
                return await self._do_download(ann)

        tasks = [_download_one(a) for a in announcements]
        results: list[Announcement] = []
        with Progress() as progress:
            task_id = progress.add_task("下载中...", total=len(tasks))
            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                progress.update(task_id, advance=1)
        return results

    async def _do_download(self, ann: Announcement) -> Announcement:
        if self._stop_event.is_set():
            ann.status = "skipped"
            return ann

        filename = f"{ann.stock_code}_{ann.announcement_id}_{safe_filename(ann.title)}.pdf"
        filepath = Path(self._download_dir) / filename

        if filepath.exists():
            ann.status = "skipped"
            return ann

        url = ann.pdf_url
        if not (
            url.startswith("https://static.cninfo.com.cn/")
            or url.startswith("https://www.cninfo.com.cn/")
        ):
            ann.status = "failed"
            ann.error = "域名校验失败"
            return ann

        content = await self._fetch_with_retry(url)
        if content is None and self._stop_event.is_set():
            ann.status = "failed"
            ann.error = "触发限流 (403)"
            return ann

        if content == b"":
            backup = self._backup_url(ann)
            content = await self._fetch_with_retry(backup)
            if content is None and self._stop_event.is_set():
                ann.status = "failed"
                ann.error = "触发限流 (403)"
                return ann

        if content is None or content == b"":
            ann.status = "failed"
            ann.error = "下载失败"
            return ann

        content_type_ok = False
        if content:
            content_type_ok = content[:5] == b"%PDF-"

        if not content_type_ok:
            ann.status = "failed"
            ann.error = "PDF 校验失败"
            return ann

        try:
            part_path = filepath.with_suffix(".part")
            part_path.write_bytes(content)
            part_path.rename(filepath)
        except OSError as e:
            raise FileSystemError(f"写入文件失败: {e}") from e

        ann.status = "downloaded"
        ann.pdf_path = str(filepath)
        return ann

    async def _fetch_with_retry(self, url: str) -> bytes | None:
        for attempt in range(3):
            try:
                content = await self._client.get_bytes(url)
                return content
            except RateLimitError:
                self._stop_event.set()
                return None
            except (NetworkError, ApiError):
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                    continue
                return None

    def _backup_url(self, ann: Announcement) -> str:
        path = ann.pdf_url.rsplit("/", 2)
        bulletin_id = path[-1].replace(".PDF", "").replace(".pdf", "")
        announce_time = path[-2]
        return f"{self._settings.cninfo_base_url}/new/announcement/download?bulletinId={bulletin_id}&announceTime={announce_time}"

    async def _write_failed(self, announcements: list[Announcement]) -> None:
        failed = [a for a in announcements if a.status == "failed"]
        if not failed:
            return
        payload = {
            "failed_count": len(failed),
            "failed_downloads": [
                {
                    "stock_code": a.stock_code,
                    "stock_name": a.stock_name,
                    "title": a.title,
                    "pdf_url": a.pdf_url,
                    "error": a.error,
                }
                for a in failed
            ],
        }
        out = Path(self._output_dir) / "failed_downloads.json"
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _build_tracker(self, announcements: list[Announcement]) -> DownloadTracker:
        tracker = DownloadTracker(total=len(announcements))
        for a in announcements:
            if a.status == "downloaded":
                tracker.success += 1
                if a.pdf_path:
                    try:
                        tracker.total_bytes += Path(a.pdf_path).stat().st_size
                    except OSError:
                        pass
            elif a.status == "failed":
                tracker.failed += 1
            elif a.status == "skipped":
                tracker.skipped += 1
        return tracker
