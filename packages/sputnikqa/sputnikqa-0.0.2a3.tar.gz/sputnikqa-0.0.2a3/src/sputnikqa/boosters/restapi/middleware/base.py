class BaseMiddleware:
    def before_request(self, method: str, url: str, kwargs: dict) -> tuple[str, str, dict]:
        """
        Вызывается перед отправкой запроса.
        Можно менять method, url, kwargs (например, добавлять хедеры).
        """
        return method, url, kwargs

    def after_response(self, response):
        """
        Вызывается после получения ответа.
        Можно обернуть его, залогировать или модифицировать.
        """
        return response
