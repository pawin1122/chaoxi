from __future__ import annotations

from datetime import datetime

from chaoxi.cli.params import QueryConfig
from chaoxi.exceptions import StockNotFoundError
from chaoxi.http_client import CninfoClient
from chaoxi.models import Announcement, AnnouncementList, QueryMeta
from chaoxi.query.dedup import (
    CST,
    clean_title,
    deduplicate,
    epoch_ms_to_beijing,
    filter_by_keyword,
    filter_exclude_keywords,
)
from chaoxi.query.fetcher import AnnouncementFetcher
from chaoxi.query.orgid import OrgIdCache
from chaoxi.utils.config import AppSettings


class QueryEngine:
    def __init__(
        self,
        config: QueryConfig,
        settings: AppSettings,
        client: CninfoClient,
    ) -> None:
        self._config = config
        self._settings = settings
        self._client = client
        self._orgid_cache = OrgIdCache(settings, client)
        self._fetcher = AnnouncementFetcher(client, config, settings)

    async def execute(self) -> AnnouncementList:
        org_ids = await self._resolve_org_ids()

        raw_announcements = await self._fetcher.fetch(org_ids)
        api_total = self._fetcher.first_page_total
        truncated = self._fetcher.was_truncated
        raw_count_before = len(raw_announcements)

        if self._config.board in ("创业板", "科创板"):
            board_page_column = {"创业板": "SZCY", "科创板": "SHKCB"}
            target = board_page_column[self._config.board]
            raw_announcements = [a for a in raw_announcements if a.page_column == target]

        for a in raw_announcements:
            a.announcement_title = clean_title(a.announcement_title)

        raw_announcements = [a for a in raw_announcements if a.adjunct_type == "PDF"]

        deduped = deduplicate(raw_announcements)

        if self._config.keyword:
            keyword_filtered = filter_by_keyword(deduped, self._config.keyword)
        else:
            keyword_filtered = deduped

        exclude_words = self._settings.exclude_keywords_list
        final = filter_exclude_keywords(keyword_filtered, exclude_words)

        if len(final) > self._config.max_results:
            final = final[: self._config.max_results]

        announcements: list[Announcement] = []
        for a in final:
            announcements.append(
                Announcement(
                    stock_code=a.sec_code,
                    stock_name=a.sec_name,
                    title=a.announcement_title,
                    short_title=a.short_title,
                    announcement_id=a.announcement_id,
                    announcement_time=epoch_ms_to_beijing(a.announcement_time),
                    announcement_type=a.announcement_type,
                    pdf_url=f"{self._settings.cninfo_static_url}/{a.adjunct_url}",
                    adjunct_size=a.adjunct_size,
                )
            )

        total_filtered = raw_count_before - len(announcements)

        return AnnouncementList(
            query=QueryMeta(
                start=str(self._config.start_date),
                end=str(self._config.end_date),
                codes=self._config.stock_codes,
                categories=self._config.categories,
                total=len(announcements),
                total_raw=raw_count_before,
                total_filtered=total_filtered,
                api_total=api_total,
                truncated=truncated,
                fetched_at=datetime.now(CST).isoformat(),
            ),
            announcements=announcements,
        )

    async def _resolve_org_ids(self) -> dict[str, dict]:
        if not self._config.stock_codes:
            return {}
        results = await self._orgid_cache.batch_get(self._config.stock_codes)
        valid: dict[str, dict] = {}
        failed: list[str] = []
        for code in self._config.stock_codes:
            info = results.get(code)
            if info:
                valid[code] = info
            else:
                failed.append(code)
        if failed and not valid:
            raise StockNotFoundError(f'未找到股票 "{", ".join(failed)}"，请检查代码是否正确。')
        if failed:
            print(f"警告：部分股票代码未找到 orgId: {', '.join(failed)}")
        return valid
