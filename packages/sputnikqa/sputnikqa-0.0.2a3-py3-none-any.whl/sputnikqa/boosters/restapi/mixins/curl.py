import httpx


class CurlFormattingMixin:
    @staticmethod
    def format_request_as_curl(request: httpx.Request) -> str:
        """Генерирует cURL-команду из httpx.Request."""
        parts = [f"curl -X {request.method} \\"]

        # Заголовки
        for key, value in request.headers.items():
            # Экранируем кавычки в значениях
            safe_value = str(value).replace('"', '\\"')
            parts.append(f'  -H "{key}: {safe_value}" \\')

        # Тело запроса
        if request.content:
            try:
                # Попробуем декодировать как UTF-8 (для JSON, form и т.д.)
                body = request.content.decode("utf-8")
                # Экранируем кавычки и переносы строк
                body = body.replace('"', '\\"').replace("\n", "\\n")
                parts.append(f'  --data "{body}" \\')
            except UnicodeDecodeError:
                # Бинарные данные — пропускаем или указываем как [binary]
                parts.append("  --data-binary @[binary_data] \\")

        # URL в конце
        parts.append(f'  "{request.url}"')

        return "\n".join(parts)
