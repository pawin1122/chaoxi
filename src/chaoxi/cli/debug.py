from __future__ import annotations

import json
from datetime import date, timedelta as td

from rich.console import Console

from chaoxi.exceptions import ValidationError
from chaoxi.http_client import CninfoClient

console = Console()


class Debugger:
    def __init__(self, client: CninfoClient):
        self._client = client

    async def test_page(self):
        try:
            resp = await self._client._client.head("/new/index")
            if resp.status_code == 200:
                console.print(f"HTTP 200 OK — cninfo 连通正常")
            else:
                console.print(f"请求失败 HTTP {resp.status_code}")
        except Exception as e:
            console.print(f"[red]请求失败: {e}[/]")

    async def inspect_api(self):
        end_date = date.today()
        start_date = end_date - td(days=3)
        max_expand = 30
        for offset in range(max_expand):
            se_date = f"{start_date.isoformat()}~{end_date.isoformat()}"
            try:
                resp = await self._client.post_form(
                    "hisAnnouncement/query",
                    {
                        "stock": "000001,gssz0000001",
                        "pageSize": "5",
                        "seDate": se_date,
                    },
                )
                announcements = (
                    resp.get("classifiedAnnouncements")
                    or resp.get("announcements")
                    or []
                )
                total = resp.get("totalRecordNum") or resp.get("totalAnnouncement") or 0
                if announcements or total:
                    console.print(
                        json.dumps(resp, indent=2, ensure_ascii=False)
                    )
                    return
            except Exception as e:
                console.print(f"[red]请求失败: {e}[/]")
                return
            start_date = start_date - td(days=1)
        console.print("[yellow]最近30天内无公告记录[/]")

    async def list_headers(self):
        console.print("请求头：")
        for key, value in self._client._client.headers.items():
            console.print(f"  {key}: {value}")

    async def run(self, action: str):
        if action == "test-page":
            await self.test_page()
        elif action == "inspect-api":
            await self.inspect_api()
        elif action == "list-headers":
            await self.list_headers()
        else:
            raise ValidationError(
                f'未知调试动作 "{action}"。',
                suggestion="可用：test-page / inspect-api / list-headers",
            )
