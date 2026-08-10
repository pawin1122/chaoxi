from __future__ import annotations

import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from chaoxi.exceptions import FileSystemError
from chaoxi.models import AnnouncementList
from chaoxi.utils.config import AppSettings


class OutputFormatter:
    def __init__(
        self,
        settings: AppSettings,
        output_dir: str | None,
        json_stdout: bool,
    ) -> None:
        self._settings = settings
        self._output_dir = output_dir
        self._json_stdout = json_stdout
        self._console = Console()

    async def output(self, result: AnnouncementList) -> None:
        if self._json_stdout:
            self._stdout_json(result)
        elif self._output_dir:
            self._json_file_output(result)
            self._table_preview(result)
        else:
            self._table_preview(result)

    def _table_preview(
        self, result: AnnouncementList, max_rows: int = 30
    ) -> None:
        table = Table(
            title="公告预览",
            title_style="bold white",
            header_style="bold cyan",
            border_style="dim",
        )
        table.add_column("代码", max_width=8, no_wrap=True)
        table.add_column("简称", max_width=12, no_wrap=True)
        table.add_column("标题", max_width=60)
        table.add_column("日期", max_width=10, no_wrap=True)
        table.add_column("大小", max_width=8, no_wrap=True)
        table.add_column("提取", max_width=8, no_wrap=True)

        sorted_announcements = sorted(
            result.announcements,
            key=lambda a: a.announcement_time,
            reverse=True,
        )

        display = sorted_announcements[:max_rows]
        for a in display:
            title = a.title
            if len(title) > 60:
                title = title[:59] + "…"
            stock_name = a.stock_name
            if len(stock_name) > 12:
                stock_name = stock_name[:11] + "…"

            table.add_row(
                a.stock_code,
                stock_name,
                title,
                a.announcement_time,
                self._format_size(a.adjunct_size * 1024),
                self._format_extraction(a.extraction),
            )

        self._console.print(table)

        total = len(sorted_announcements)
        if total > max_rows:
            self._console.print(
                f"[dim]仅显示前 {max_rows} 条，共 {total} 条[/dim]"
            )
        else:
            self._console.print(f"[dim]共 {total} 条[/dim]")

        if result.query.truncated:
            self._console.print(
                "[yellow]⚠ 查询结果已达翻页上限(3000条)，部分公告可能未包含[/yellow]"
            )

        if any(a.status for a in result.announcements):
            self._print_download_summary(result)

        if any(a.extraction for a in result.announcements):
            self._print_extract_summary(result)

    def _json_file_output(self, result: AnnouncementList) -> None:
        output_path = Path(self._output_dir) / "announcements.json"
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise FileSystemError(f"无法创建输出目录 {self._output_dir}: {e}") from e

        try:
            output_path.write_text(
                result.model_dump_json(indent=2), encoding="utf-8"
            )
        except OSError as e:
            raise FileSystemError(f"无法写入JSON文件: {e}") from e

        self._console.print(
            f"[green]JSON 已写入 {output_path}[/green]"
        )

    def _stdout_json(self, result: AnnouncementList) -> None:
        print(result.model_dump_json(indent=2), file=sys.stdout)

    def _print_download_summary(self, result: AnnouncementList) -> None:
        success = sum(
            1 for a in result.announcements if a.status == "downloaded"
        )
        failed = sum(
            1 for a in result.announcements if a.status == "failed"
        )
        skipped = sum(
            1 for a in result.announcements if a.status == "skipped"
        )
        total_kb = sum(
            a.adjunct_size for a in result.announcements if a.status == "downloaded"
        )
        size_str = self._format_size(int(total_kb * 1024))
        self._console.print(
            f"下载: {success} 成功 / {failed} 失败 / {skipped} 跳过 / 共 {size_str}"
        )

    @staticmethod
    def _format_size(size: int) -> str:
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f}KB"
        else:
            return f"{size / (1024 * 1024):.1f}MB"

    @staticmethod
    def _format_extraction(extraction: dict | None) -> str:
        if extraction is None:
            return "[dim]-[/dim]"
        status = extraction.get("status")
        if status == "success":
            return "[green]✅[/green]"
        elif status == "partial":
            garbled_pages = extraction.get("garbled_pages", [])
            n = len(garbled_pages)
            return f"[yellow]⚠️{n}页[/yellow]"
        elif status == "failed":
            pdf_type = extraction.get("pdf_type", "")
            if pdf_type in ("scanned", "image_based"):
                return "[red]❌扫描件[/red]"
            else:
                return "[red]❌不可提取[/red]"
        elif status == "error":
            return "[red]❌错误[/red]"
        return "[dim]-[/dim]"

    def _print_extract_summary(self, result: AnnouncementList) -> None:
        success = sum(
            1 for a in result.announcements
            if a.extraction and a.extraction.get("status") == "success"
        )
        partial = sum(
            1 for a in result.announcements
            if a.extraction and a.extraction.get("status") == "partial"
        )
        failed = sum(
            1 for a in result.announcements
            if a.extraction and a.extraction.get("status") == "failed"
        )
        error = sum(
            1 for a in result.announcements
            if a.extraction and a.extraction.get("status") == "error"
        )
        self._console.print(
            f"提取: [green]{success} 成功[/green] / "
            f"[yellow]{partial} 部分[/yellow] / "
            f"[red]{failed + error} 失败[/red]"
        )
