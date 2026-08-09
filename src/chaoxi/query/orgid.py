from __future__ import annotations

import asyncio

from chaoxi.exceptions import StockNotFoundError
from chaoxi.http_client import CninfoClient
from chaoxi.utils.config import AppSettings


class OrgIdCache:
    def __init__(self, settings: AppSettings, client: CninfoClient) -> None:
        self._settings = settings
        self._client = client
        self._cache: dict[str, dict] = {}

    async def get(self, code: str) -> dict:
        if code in self._cache:
            return self._cache[code]
        info = await self._fetch_orgid_from_api(code)
        self._cache[code] = info
        return info

    async def batch_get(self, codes: list[str]) -> dict[str, dict]:
        results: dict[str, dict] = {}
        uncached: list[str] = []
        for code in codes:
            if code in self._cache:
                results[code] = self._cache[code]
            else:
                uncached.append(code)

        if not uncached:
            return results

        tasks = {code: asyncio.create_task(self._fetch_orgid_from_api(code)) for code in uncached}

        for code, task in tasks.items():
            try:
                info = await task
                self._cache[code] = info
                results[code] = info
            except StockNotFoundError:
                pass

        return results

    async def _fetch_orgid_from_api(self, code: str) -> dict:
        data = await self._client.post_form(
            f"/information/topSearch/query?keyWord={code}",
            {},
        )

        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            items = data.get("data", data.get("results", []))
        else:
            items = []

        if not items:
            raise StockNotFoundError(f'未找到股票 "{code}"，请检查代码是否正确。')

        for item in items:
            if item.get("code") == code:
                org_id = item["orgId"]
                name = item.get("zwjc", "")
                board = self._derive_board(org_id)
                return {"orgId": org_id, "name": name, "board": board}

        raise StockNotFoundError(f'未找到股票 "{code}"，请检查代码是否正确。')

    @staticmethod
    def _derive_board(org_id: str) -> str:
        if org_id.startswith("gssz"):
            return "sz"
        if org_id.startswith("gssh"):
            return "sh"
        if org_id.startswith("gsbj"):
            return "bj"
        return "sz"
