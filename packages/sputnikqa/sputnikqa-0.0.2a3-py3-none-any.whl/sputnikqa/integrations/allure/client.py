from ...boosters.restapi.clients.api_client import ApiClient
from ...boosters.restapi.types import HttpResponse

try:
    import allure
except ImportError:
    raise ImportError(
        "Allure integration requires 'allure-python-commons'. "
        "Install with: pip install sputnikqa[allure]"
    )


class ApiClientAllure(ApiClient[HttpResponse]):

    @allure.step('{method} {url}')
    def request(self, method: str, url: str, **kwargs) -> HttpResponse:
        return super().request(method, url, **kwargs)
