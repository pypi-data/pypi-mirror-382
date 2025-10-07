from ...boosters.restapi.middleware.base import BaseMiddleware
from ...boosters.restapi.mixins.curl import CurlFormattingMixin
from ...boosters.restapi.types import HttpResponse

try:
    import allure
except ImportError:
    raise ImportError(
        "Allure integration requires 'allure-python-commons'. "
        "Install with: pip install sputnikqa[allure]"
    )


class AllureMiddleware(BaseMiddleware, CurlFormattingMixin):

    def after_response(self, response: HttpResponse) -> HttpResponse:
        if allure is None:
            return response

        # Прикрепляем данные к Allure
        allure.attach(
            str(response.status_code),
            name="status_code",
            attachment_type=allure.attachment_type.TEXT
        )
        allure.attach(
            str(response.text),
            name="response_body",
            attachment_type=allure.attachment_type.TEXT
        )
        allure.attach(
            self.format_request_as_curl(response.request),
            name="curl",
            attachment_type=allure.attachment_type.TEXT
        )

        return response
