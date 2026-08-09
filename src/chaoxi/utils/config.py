from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    cninfo_base_url: str = "https://www.cninfo.com.cn/new"
    cninfo_static_url: str = "https://static.cninfo.com.cn"
    cninfo_timeout: int = 30
    default_lookback_days: int = 90
    max_pages: int = 100
    max_concurrent: int = 4
    request_interval: float = 0.5
    download_confirm_threshold: int = 50
    chaoxi_output_dir: str = "./chaoxi_output"
    max_log_lines: int = 500
    exclude_keywords: str = "摘要,确认意见,取消,更正,补充,提示,致歉,修订,英文"
    http_proxy: str | None = None
    https_proxy: str | None = None

    @property
    def exclude_keywords_list(self) -> list[str]:
        return [kw.strip() for kw in self.exclude_keywords.split(",") if kw.strip()]


@lru_cache()
def get_settings() -> AppSettings:
    return AppSettings()
