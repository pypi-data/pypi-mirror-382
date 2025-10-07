from typing import Generic

from .base import BaseHttpClient, BaseAsyncHttpClient
from ..middleware.base import BaseMiddleware
from ..types import HttpResponse


class ApiClient(Generic[HttpResponse]):
    def __init__(self, http_client: BaseHttpClient[HttpResponse], middlewares: list[BaseMiddleware] | None = None):
        self._http_client = http_client
        self._middlewares = middlewares or []

    def request(self, method: str, url: str, **kwargs) -> HttpResponse:
        # прогон через pre-request цепочку
        for m in self._middlewares:
            method, url, kwargs = m.before_request(method, url, kwargs)

        response = self._http_client.request(method, url, **kwargs)

        # прогон через post-response цепочку
        for m in self._middlewares:
            response = m.after_response(response)

        return response

    def get(self, url: str, **kwargs) -> HttpResponse:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> HttpResponse:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs) -> HttpResponse:
        return self.request("PUT", url, **kwargs)

    def patch(self, url: str, **kwargs) -> HttpResponse:
        return self.request('PATCH', url, **kwargs)

    def delete(self, url: str, **kwargs) -> HttpResponse:
        return self.request("DELETE", url, **kwargs)

    def head(self, url: str, **kwargs) -> HttpResponse:
        return self.request('HEAD', url, **kwargs)

    def options(self, url: str, **kwargs) -> HttpResponse:
        return self.request('OPTIONS', url, **kwargs)


class AsyncApiClient(Generic[HttpResponse]):
    def __init__(self, http_client: BaseAsyncHttpClient[HttpResponse],
                 middlewares: list[BaseMiddleware] | None = None):
        self._http_client = http_client
        self._middlewares = middlewares or []

    async def request(self, method: str, url: str, **kwargs) -> HttpResponse:
        # Прогон через pre-request middleware
        for m in self._middlewares:
            method, url, kwargs = m.before_request(method, url, kwargs)
        response = await self._http_client.request(method, url, **kwargs)
        # Прогон через post-response middleware
        for m in self._middlewares:
            response = m.after_response(response)
        return response

    async def get(self, url: str, **kwargs) -> HttpResponse:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> HttpResponse:
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> HttpResponse:
        return await self.request("PUT", url, **kwargs)

    async def patch(self, url: str, **kwargs) -> HttpResponse:
        return await self.request('PATCH', url, **kwargs)

    async def delete(self, url: str, **kwargs) -> HttpResponse:
        return await self.request("DELETE", url, **kwargs)

    async def head(self, url: str, **kwargs) -> HttpResponse:
        return await self.request('HEAD', url, **kwargs)

    async def options(self, url: str, **kwargs) -> HttpResponse:
        return await self.request('OPTIONS', url, **kwargs)
