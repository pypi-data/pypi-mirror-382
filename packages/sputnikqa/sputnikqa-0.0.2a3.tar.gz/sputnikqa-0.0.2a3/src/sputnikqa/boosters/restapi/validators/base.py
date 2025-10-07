from typing import Generic, Type

from ..types import HttpResponse
from ..response_models import JsonResponse, PrimitiveResponse, EmptyResponse


class BaseApiResponseValidator(Generic[HttpResponse]):
    def __init__(self, response: HttpResponse):
        self.response = response
        self.parsed_model = None

    def validate_status(self, expected_status: int | tuple[int, ...]):
        if isinstance(expected_status, tuple):
            assert self.response.status_code in expected_status, f"Expected {expected_status}, got {self.response.status_code}"
        else:
            assert self.response.status_code == expected_status, f"Expected {expected_status}, got {self.response.status_code}"
        return self

    def validate_response_model(self, models: dict[int | tuple[int, ...], Type[JsonResponse] | Type[PrimitiveResponse]]):
        model_class = None

        # Ищем подходящую модель
        for key, model in models.items():
            if (isinstance(key, int) and key == self.response.status_code) or \
                    (isinstance(key, tuple) and self.response.status_code in key):
                model_class = model
                break

        if model_class:
            if issubclass(model_class, PrimitiveResponse):
                if issubclass(model_class, EmptyResponse):
                    if self.response.text.strip() == '':
                        self.parsed_model = model_class.model_validate({"data": None})
                    else:
                        raise ValueError(
                            f"Expected empty response for EmptyResponse model, but got: {self.response.text[:200]}..."
                        )
                else:
                    self.parsed_model = model_class.model_validate({"data": self.response.json()})
            else:
                self.parsed_model = model_class.model_validate(self.response.json())
        else:
            raise ValueError(f"No model for status code {self.response.status_code}")
        return self

    def get_validated_model(self):
        """Возвращает валидированное значение.
        Для PrimitiveResponse  -> .data,
        для JsonResponse    -> саму модель.
        """
        if self.parsed_model is None:
            raise ValueError("Model not validated. Call validate_response_model() first.")

        if isinstance(self.parsed_model, PrimitiveResponse):
            return self.parsed_model.data

        return self.parsed_model

    def get_raw_response(self) -> HttpResponse:
        """Возвращает исходный HTTP-ответ"""
        return self.response