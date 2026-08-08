from __future__ import annotations

import asyncio
import random

import httpx

from chaoxi.exceptions import ApiError, NetworkError, RateLimitError
from chaoxi.utils.config import AppSettings


class CninfoClient:
    def __init__(self, settings: AppSettings):
        self._settings = settings
        self._base = settings.cninfo_base_url
        self._semaphore = asyncio.Semaphore(settings.max_concurrent)

        timeout = httpx.Timeout(settings.cninfo_timeout)
        proxy = settings.https_proxy or settings.http_proxy
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/150.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        self._client = httpx.AsyncClient(
            base_url=self._base,
            timeout=timeout,
            proxy=proxy,
            headers=headers,
            follow_redirects=True,
        )

    async def __aenter__(self) -> CninfoClient:
        await self._init_cookies()
        return self

    async def __aexit__(self, *args: object) -> None:
        await self._client.aclose()

    async def _init_cookies(self) -> None:
        await self._client.get("/new/index")

    async def post_form(self, path: str, data: dict[str, str]) -> dict:
        async with self._semaphore:
            await asyncio.sleep(random.uniform(0.5, 1.5))
            for attempt in range(3):
                try:
                    resp = await self._client.post(path, data=data)
                    if resp.status_code == 403:
                        raise RateLimitError(
                            "检测到限流 (HTTP 403)，建议等待 5-10 分钟后重试。"
                        )
                    if resp.status_code >= 500:
                        if attempt < 2:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        raise ApiError(
                            f"服务器错误 HTTP {resp.status_code}", resp.status_code
                        )
                    if resp.status_code >= 400:
                        raise ApiError(
                            f"请求失败 HTTP {resp.status_code}", resp.status_code
                        )
                    return resp.json()
                except (httpx.TimeoutException, httpx.ConnectError):
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise NetworkError(
                        f"网络错误（已重试{attempt + 1}次）", retries=attempt + 1
                    )
            raise NetworkError("网络错误（重试耗尽）")

    async def get_json(
        self, path: str, params: dict[str, str] | None = None
    ) -> dict:
        async with self._semaphore:
            await asyncio.sleep(random.uniform(0.5, 1.5))
            for attempt in range(3):
                try:
                    resp = await self._client.get(path, params=params)
                    if resp.status_code == 403:
                        raise RateLimitError(
                            "检测到限流 (HTTP 403)，建议等待 5-10 分钟后重试。"
                        )
                    if resp.status_code >= 500:
                        if attempt < 2:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        raise ApiError(
                            f"服务器错误 HTTP {resp.status_code}", resp.status_code
                        )
                    if resp.status_code >= 400:
                        raise ApiError(
                            f"请求失败 HTTP {resp.status_code}", resp.status_code
                        )
                    return resp.json()
                except (httpx.TimeoutException, httpx.ConnectError):
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise NetworkError(
                        f"网络错误（已重试{attempt + 1}次）", retries=attempt + 1
                    )
            raise NetworkError("网络错误（重试耗尽）")

    async def get_bytes(self, url: str) -> bytes:
        async with self._semaphore:
            await asyncio.sleep(random.uniform(0.5, 1.5))
            for attempt in range(3):
                try:
                    resp = await self._client.get(url)
                    if resp.status_code == 403:
                        raise RateLimitError(
                            "检测到限流 (HTTP 403)，建议等待 5-10 分钟后重试。"
                        )
                    if resp.status_code >= 500:
                        if attempt < 2:
                            await asyncio.sleep(2 ** attempt)
                            continue
                        raise ApiError(
                            f"服务器错误 HTTP {resp.status_code}", resp.status_code
                        )
                    if resp.status_code == 404:
                        return b""
                    if resp.status_code >= 400:
                        raise ApiError(
                            f"请求失败 HTTP {resp.status_code}", resp.status_code
                        )
                    return resp.content
                except (httpx.TimeoutException, httpx.ConnectError):
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise NetworkError(
                        f"网络错误（已重试{attempt + 1}次）", retries=attempt + 1
                    )
            raise NetworkError("网络错误（重试耗尽）")
