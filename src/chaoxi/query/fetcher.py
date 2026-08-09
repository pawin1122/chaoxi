from __future__ import annotations

import asyncio

from chaoxi.cli._constants import BOARD_MAP, CATEGORY_NAME_MAP
from chaoxi.cli.params import QueryConfig
from chaoxi.http_client import CninfoClient
from chaoxi.models import RawAnnouncement
from chaoxi.utils.config import AppSettings


class AnnouncementFetcher:
    def __init__(
        self,
        client: CninfoClient,
        config: QueryConfig,
        settings: AppSettings,
    ) -> None:
        self._client = client
        self._config = config
        self._settings = settings
        self._first_page_total: int = 0
        self._was_truncated: bool = False

    @property
    def first_page_total(self) -> int:
        return self._first_page_total

    @property
    def was_truncated(self) -> bool:
        return self._was_truncated

    async def fetch(self, org_ids: dict[str, dict]) -> list[RawAnnouncement]:
        category = self._build_category()
        columns, plate = self._resolve_columns()

        stock = ""
        if org_ids:
            parts = [f"{code},{org_ids[code]['orgId']}" for code in self._config.stock_codes if code in org_ids]
            stock = ";".join(parts)

        keyword = self._config.keyword or ""

        se_date = f"{self._config.start_date}~{self._config.end_date}"
        show_progress = self._config.verbose

        results: list[RawAnnouncement] = []

        column_tasks = [
            self._fetch_one_column(col, stock, category, se_date, plate or "", keyword)
            for col in columns
        ]
        batch_results = await asyncio.gather(*column_tasks)
        for batch in batch_results:
            results.extend(batch)
        if show_progress:
            print(f"\r查询中 {len(results)} 条...", end="", flush=True)

        if show_progress:
            print()

        return results

    async def _fetch_one_column(
        self,
        column: str,
        stock: str,
        category: str,
        se_date: str,
        plate: str,
        keyword: str,
    ) -> list[RawAnnouncement]:
        results: list[RawAnnouncement] = []
        page = 1
        while True:
            data = await self._client.post_form(
                "/hisAnnouncement/query",
                self._build_form_data(page, column, stock, category, se_date, plate, keyword),
            )
            if page == 1:
                self._first_page_total = int(data.get("totalAnnouncement", 0))
            announcements = data.get("announcements") or []
            batch = [RawAnnouncement(**item) for item in announcements]
            if not batch:
                break
            results.extend(batch)
            page += 1
            if page > self._settings.max_pages:
                self._was_truncated = True
                break
            if not data.get("hasMore", True):
                break
        return results

    def _build_category(self) -> str:
        cats = self._config.categories
        if not cats:
            return ";".join(CATEGORY_NAME_MAP.values())
        return ";".join(CATEGORY_NAME_MAP[c] for c in cats if c in CATEGORY_NAME_MAP)

    def _resolve_columns(self) -> tuple[list[str], str | None]:
        board = self._config.board
        if board and board in BOARD_MAP:
            col, plat = BOARD_MAP[board]
            return [col], plat
        return ["szse", "sse"], None

    @staticmethod
    def _build_form_data(
        page_num: int,
        column: str,
        stock: str,
        category: str,
        se_date: str,
        plate: str,
        keyword: str,
    ) -> dict[str, str]:
        return {
            "pageNum": str(page_num),
            "pageSize": "30",
            "column": column,
            "tabName": "fulltext",
            "plate": plate,
            "stock": stock,
            "searchkey": keyword,
            "secid": "",
            "category": category,
            "trade": "",
            "seDate": se_date,
            "sortName": "",
            "sortType": "",
            "isHLtitle": "true",
        }
