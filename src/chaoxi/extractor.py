from __future__ import annotations

import re
from pathlib import Path

from pdf_inspector import PdfResult, process_pdf
from pydantic import BaseModel
from rich.progress import Progress

from chaoxi.models import Announcement
from chaoxi.utils.config import AppSettings

_ILLEGAL_CHARS_RE = re.compile(r'[/:*?"<>|]')


def safe_filename(title: str) -> str:
    return _ILLEGAL_CHARS_RE.sub("_", title)


class ExtractionTracker(BaseModel):
    total: int = 0
    success: int = 0
    partial: int = 0
    failed: int = 0
    error: int = 0
    total_pages: int = 0


class PdfExtractor:
    def __init__(self, settings: AppSettings, output_dir: str):
        self._settings = settings
        self._output_dir = output_dir

    async def extract(
        self, announcements: list[Announcement]
    ) -> tuple[list[Announcement], ExtractionTracker]:
        pending = [
            a
            for a in announcements
            if a.status == "downloaded" and a.pdf_path and Path(a.pdf_path).exists()
        ]
        if not pending:
            tracker = ExtractionTracker(total=len(announcements))
            return announcements, tracker

        md_dir = Path(self._output_dir) / "md"
        md_dir.mkdir(parents=True, exist_ok=True)

        with Progress() as progress:
            task_id = progress.add_task("提取中...", total=len(pending))
            for ann in pending:
                self._do_extract(ann, md_dir)
                progress.update(task_id, advance=1)

        original_order = {id(a): i for i, a in enumerate(announcements)}
        announcements.sort(key=lambda a: original_order.get(id(a), 9999))

        tracker = self._build_tracker(announcements)
        return announcements, tracker

    def _do_extract(self, ann: Announcement, md_dir: Path) -> None:
        filename = f"{ann.stock_code}_{ann.announcement_id}_{safe_filename(ann.title)}.md"
        md_path = md_dir / filename

        try:
            result: PdfResult = process_pdf(ann.pdf_path)
        except Exception as e:
            ann.error = str(e)
            ann.md_path = None
            ann.extraction = {"status": "error", "error": str(e)}
            return

        pdf_type = result.pdf_type

        if pdf_type in ("scanned", "image_based"):
            ann.md_path = None
            ann.extraction = {"status": "failed", "pdf_type": pdf_type, "page_count": result.page_count}
            return

        if result.has_encoding_issues:
            ann.extraction = {
                "status": "partial",
                "pdf_type": pdf_type,
                "garbled_pages": result.pages_needing_ocr,
                "page_count": result.page_count,
            }
        else:
            ann.extraction = {"status": "success", "pdf_type": pdf_type, "page_count": result.page_count}

        try:
            md_path.write_text(result.markdown, encoding="utf-8")
        except OSError as e:
            ann.error = str(e)
            ann.md_path = None
            ann.extraction = {"status": "error", "error": str(e)}
            return

        ann.md_path = str(md_path.relative_to(self._output_dir))

    @staticmethod
    def _build_tracker(announcements: list[Announcement]) -> ExtractionTracker:
        tracker = ExtractionTracker(total=len(announcements))
        for a in announcements:
            if not a.extraction:
                continue
            ext_status = a.extraction.get("status")
            if ext_status == "success":
                tracker.success += 1
            elif ext_status == "partial":
                tracker.partial += 1
            elif ext_status == "failed":
                tracker.failed += 1
            elif ext_status == "error":
                tracker.error += 1
            if "page_count" in a.extraction:
                tracker.total_pages += a.extraction["page_count"]
        return tracker
