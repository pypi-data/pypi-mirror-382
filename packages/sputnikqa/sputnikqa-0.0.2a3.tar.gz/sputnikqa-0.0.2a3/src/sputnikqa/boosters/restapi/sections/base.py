from typing import Generic, Type
from urllib.parse import urljoin, urlparse

from ..clients.api_client import ApiClient
from ..types import HttpResponse
from ..validators.base import BaseApiResponseValidator


class BaseApiSection(Generic[HttpResponse]):
    base_url = None

    def __init__(self,
                 client: ApiClient[HttpResponse],
                 validator_class: Type[BaseApiResponseValidator] = BaseApiResponseValidator
                 ):
        self.client: ApiClient[HttpResponse] = client
        self.validator_class: Type[BaseApiResponseValidator] = validator_class
        self._base_headers: dict = {}

    def url_join(self, path: str, base: str = None):
        if not base:
            if self.base_url:
                base = self.base_url
            else:
                raise ValueError("base_url is not set")
        # Проверяем, что path — не абсолютный URL
        parsed = urlparse(path)
        if parsed.scheme or parsed.netloc:
            raise ValueError(f"Path '{path}' is absolute URL, cannot join safely")
        if path:
            base = base.rstrip('/') + '/'
        return urljoin(base, path)

    def validator(self, response: HttpResponse) -> BaseApiResponseValidator[HttpResponse]:
        return self.validator_class(response)

    @property
    def base_headers(self) -> dict:
        return self._base_headers

    @base_headers.setter
    def base_headers(self, headers: dict[str, str]):
        self._base_headers = headers
