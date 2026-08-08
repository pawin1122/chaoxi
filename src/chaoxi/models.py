from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RawAnnouncement(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    sec_code: str = Field(alias="secCode")
    sec_name: str = Field(alias="secName")
    org_id: str = Field(alias="orgId")
    announcement_id: str = Field(alias="announcementId")
    announcement_title: str = Field(alias="announcementTitle")
    announcement_time: int = Field(alias="announcementTime")
    adjunct_url: str = Field(alias="adjunctUrl")
    adjunct_size: int = Field(alias="adjunctSize")
    adjunct_type: str = Field(alias="adjunctType")
    announcement_type: str = Field(alias="announcementType")
    page_column: str = Field(alias="pageColumn")
    short_title: str = Field(alias="shortTitle")


class Announcement(BaseModel):
    stock_code: str
    stock_name: str
    title: str
    short_title: str
    announcement_id: str
    announcement_time: str
    announcement_type: str
    pdf_url: str
    adjunct_size: int
    pdf_path: str | None = None
    status: str | None = None
    error: str | None = None


class QueryMeta(BaseModel):
    start: str
    end: str
    codes: list[str]
    categories: list[str]
    total: int
    total_raw: int
    total_filtered: int
    api_total: int = 0
    truncated: bool = False
    fetched_at: str


class AnnouncementList(BaseModel):
    query: QueryMeta
    announcements: list[Announcement]
