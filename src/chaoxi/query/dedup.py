from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from chaoxi.models import RawAnnouncement

UTC = timezone.utc
CST = timezone(timedelta(hours=8))

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def deduplicate(announcements: list[RawAnnouncement]) -> list[RawAnnouncement]:
    seen: set[tuple] = set()
    result: list[RawAnnouncement] = []
    for a in announcements:
        key = _dedup_key(a)
        if key not in seen:
            seen.add(key)
            result.append(a)
    return result


def _dedup_key(a: RawAnnouncement) -> tuple:
    return (a.sec_code, a.announcement_title.strip(), a.adjunct_url)


def filter_by_keyword(
    announcements: list[RawAnnouncement],
    keyword: str,
) -> list[RawAnnouncement]:
    if not keyword:
        return announcements
    kw = keyword.lower()
    return [
        a
        for a in announcements
        if kw in a.announcement_title.lower()
        or kw in a.short_title.lower()
    ]


def filter_exclude_keywords(
    announcements: list[RawAnnouncement],
    exclude_words: list[str],
) -> list[RawAnnouncement]:
    if not exclude_words:
        return announcements
    return [
        a
        for a in announcements
        if not any(kw in a.announcement_title for kw in exclude_words)
    ]


def clean_title(raw_title: str) -> str:
    return _HTML_TAG_RE.sub("", raw_title).strip()


def epoch_ms_to_beijing(ts: int) -> str:
    dt = datetime.fromtimestamp(ts / 1000, tz=UTC).astimezone(CST)
    return dt.strftime("%Y-%m-%d")
