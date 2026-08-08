from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from chaoxi.utils.config import AppSettings


class LogEngine:
    def __init__(self, settings: AppSettings):
        self._log_dir = Path(settings.chaoxi_output_dir)
        self._log_path = self._log_dir / ".chaoxi.log"
        self._max_lines = settings.max_log_lines
        self._lock = asyncio.Lock()

    async def write(
        self,
        event: str,
        session_id: str,
        details: dict | None = None,
        level: str = "info",
    ) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "event": event,
            "level": level,
            "details": details or {},
        }
        async with self._lock:
            self._log_dir.mkdir(parents=True, exist_ok=True)
            with open(self._log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            self._rotate_if_needed()

    def read(self, *, tail: int = 20) -> list[dict]:
        if not self._log_path.exists():
            return []
        with open(self._log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        entries: list[dict] = []
        for line in lines[-tail:]:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return entries

    async def clear(self) -> None:
        async with self._lock:
            if self._log_path.exists():
                self._log_path.unlink()

    def _rotate_if_needed(self) -> None:
        if not self._log_path.exists():
            return
        with open(self._log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if len(lines) > self._max_lines:
            trim_count = max(1, int(self._max_lines * 0.1))
            kept = lines[trim_count:]
            with open(self._log_path, "w", encoding="utf-8") as f:
                f.writelines(kept)
