from typing import Any

from pydantic import BaseModel, ConfigDict


class JsonResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PrimitiveResponse(BaseModel):
    """Базовый класс для моделей-обёрток с полем data"""
    data: Any


class EmptyResponse(PrimitiveResponse):
    data: None = None


class BoolResponse(PrimitiveResponse):
    data: bool


class NumberResponse(PrimitiveResponse):
    data: int | float


class StringResponse(PrimitiveResponse):
    data: str


class ListResponse(PrimitiveResponse):
    data: list[Any]
