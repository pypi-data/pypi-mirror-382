from abc import ABC, abstractmethod
from typing import Generic

from ..types import HttpResponse


class BaseHttpClient(ABC, Generic[HttpResponse]):
    @abstractmethod
    def request(self, method: str, url: str, **kwargs) -> HttpResponse:
        ...


class BaseAsyncHttpClient(ABC, Generic[HttpResponse]):
    @abstractmethod
    async def request(self, method: str, url: str, **kwargs) -> HttpResponse:
        ...
