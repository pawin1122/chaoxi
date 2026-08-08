from __future__ import annotations

import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from rich.console import Console

from chaoxi.exceptions import ValidationError
from chaoxi.utils.config import AppSettings

_DIR_PATTERN = re.compile(r"^\d{8}_\d{6}$")
_SIZE_UNITS: dict[str, int] = {"K": 1000, "M": 1_000_000, "G": 1_000_000_000, "T": 1_000_000_000_000}
_TIME_UNITS: dict[str, str] = {"d": "days", "h": "hours", "m": "minutes", "s": "seconds"}

console = Console()


def _format_bytes(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1000:
            return f"{size:.1f} {unit}"
        size /= 1000
    return f"{size:.1f} PB"


class Cleaner:
    def __init__(self, settings: AppSettings):
        self._output_root = Path(settings.chaoxi_output_dir)

    def clean(
        self,
        older_than: str | None,
        max_size: str | None,
        keep: int | None,
        dry_run: bool,
    ):
        specified = sum(p is not None for p in (older_than, max_size, keep))
        if specified == 0:
            raise ValidationError(
                "请至少指定 --older-than、--max-size 或 --keep 中的一个。",
            )
        if specified > 1:
            raise ValidationError(
                "--older-than、--max-size、--keep 只能选择其一",
            )

        dirs = self._collect_dirs()
        if not dirs:
            console.print("[yellow]没有可清理的目录[/]")
            return

        to_delete: list[tuple[Path, datetime, int]] = []
        if older_than is not None:
            cutoff = datetime.now() - self._parse_timedelta(older_than)
            to_delete = [d for d in dirs if d[1] < cutoff]
        elif max_size is not None:
            max_bytes = self._parse_size(max_size)
            total = sum(d[2] for d in dirs)
            for d in dirs:
                if total <= max_bytes:
                    break
                to_delete.append(d)
                total -= d[2]
        elif keep is not None:
            if keep < 0:
                raise ValidationError("--keep 不能为负数")
            if keep == 0:
                to_delete = dirs
            else:
                delete_count = max(0, len(dirs) - keep)
                to_delete = dirs[:delete_count]

        if not to_delete:
            console.print("[green]没有需要清理的目录[/]")
            return

        total_size = sum(d[2] for d in to_delete)
        self._print_plan([d[0] for d in to_delete], total_size, dry_run)
        if not dry_run:
            self._delete_dirs([d[0] for d in to_delete])
            console.print(
                f"[green]✓ 已删除 {len(to_delete)} 个目录，释放 {_format_bytes(total_size)}[/]"
            )

    def _parse_size(self, raw: str) -> int:
        raw = raw.strip().upper()
        if raw[-1] in _SIZE_UNITS:
            return int(float(raw[:-1]) * _SIZE_UNITS[raw[-1]])
        return int(raw)

    def _parse_timedelta(self, raw: str) -> timedelta:
        m = re.match(r"^(\d+)([dhms])$", raw.strip().lower())
        if not m:
            raise ValidationError(
                f"无法解析时间格式: {raw}，支持如 30d / 24h / 60m",
            )
        value = int(m.group(1))
        unit = _TIME_UNITS[m.group(2)]
        return timedelta(**{unit: value})

    def _collect_dirs(self) -> list[tuple[Path, datetime, int]]:
        if not self._output_root.exists():
            return []
        results: list[tuple[Path, datetime, int]] = []
        for entry in sorted(self._output_root.iterdir()):
            if not entry.is_dir():
                continue
            if not _DIR_PATTERN.match(entry.name):
                continue
            dt = datetime.strptime(entry.name, "%Y%m%d_%H%M%S")
            total = sum(
                f.stat().st_size for f in entry.rglob("*") if f.is_file()
            )
            results.append((entry, dt, total))
        results.sort(key=lambda x: x[1])
        return results

    def _print_plan(self, to_delete: list[Path], total_size: int, dry_run: bool):
        if dry_run:
            prefix = f"预览模式，以下 {len(to_delete)} 个目录将被删除"
        else:
            prefix = "以下目录将被删除"
        console.print(
            f"\n{prefix}（共 {_format_bytes(total_size)}）："
        )
        for p in to_delete:
            console.print(f"  {p.name}")

    def _delete_dirs(self, dirs: list[Path]):
        for p in dirs:
            try:
                shutil.rmtree(p)
            except OSError as e:
                console.print(f"[yellow]⚠ 删除失败 {p.name}: {e}[/]")
