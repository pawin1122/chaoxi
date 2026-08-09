from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from rich.console import Console
from rich.table import Table

from chaoxi.logging import LogEngine

console = Console()


class LogViewer:
    def __init__(self, engine: LogEngine):
        self._engine = engine

    def view(
        self,
        tail: int = 20,
        today: bool = False,
        session_id: str | None = None,
        level: str | None = None,
    ):
        entries = self._engine.read(tail=tail)
        if not entries:
            console.print("[yellow]尚无日志记录[/]")
            return

        if today:
            today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            entries = [
                e
                for e in entries
                if e.get("timestamp", "").startswith(today_str)
            ]
        if session_id:
            entries = [
                e for e in entries if e.get("session_id") == session_id
            ]
        if level:
            entries = [e for e in entries if e.get("level") == level]

        if not entries:
            console.print("[yellow]无匹配的日志记录[/]")
            return

        entries.reverse()

        table = Table(title=f"日志 (最近 {tail} 条)", header_style="bold")
        table.add_column("时间", style="cyan", no_wrap=True)
        table.add_column("会话", style="dim")
        table.add_column("事件", style="white")
        table.add_column("级别", style="magenta")
        table.add_column("详情", style="dim")

        for entry in entries:
            ts = entry.get("timestamp", "")
            if ts:
                try:
                    dt = datetime.fromisoformat(ts).strftime("%m-%d %H:%M:%S")
                except ValueError:
                    dt = ts
            else:
                dt = ts
            sid = entry.get("session_id", "")
            event = entry.get("event", "")
            lvl = entry.get("level", "info")
            details = entry.get("details", {})
            if isinstance(details, dict):
                detail_str = ", ".join(
                    f"{k}={v}" for k, v in details.items()
                )
            else:
                detail_str = str(details)
            table.add_row(dt, sid, event, lvl, detail_str)

        console.print(table)

    def clear(self):
        response = input("是否清空日志？[y/N] ").strip().lower()
        if response == "y":
            asyncio.run(self._engine.clear())
            console.print("[green]日志已清空[/]")
        else:
            console.print("已取消")
