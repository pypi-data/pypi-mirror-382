import httpx

from .base import BaseHttpClient, BaseAsyncHttpClient


class HttpxClient(BaseHttpClient[httpx.Response]):
    def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        return httpx.request(method, url, **kwargs)


class AsyncHttpxClient(BaseAsyncHttpClient[httpx.Response]):
    def __init__(self):
        self._client = httpx.AsyncClient()

    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        return await self._client.request(method, url, **kwargs)

    async def close(self):
        await self._client.aclose()
