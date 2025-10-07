import mimetypes
from abc import ABC
from copy import deepcopy
from pathlib import Path
from typing import Any


class RequestDictBuilder(ABC):
    _data: dict[str, Any] = {}

    def __new__(cls, *args, **kwargs):
        if cls is RequestDictBuilder:
            raise TypeError(f"{cls.__name__} is an abstract base class and cannot be instantiated directly.")
        return super().__new__(cls)

    def build(self) -> dict[str, Any]:
        return deepcopy(self._data)

    def __repr__(self):
        return f'{self.__class__.__name__}({self._data})'


class SingleFileUploadBuilder:
    def __init__(self):
        self._field_name: str = "file"
        self._file_path: Path | None = None
        self._content_type: str | None = None
        self._file_obj = None  # будет открыт в __enter__

    def with_file(self, file_path: Path | str) -> 'SingleFileUploadBuilder':
        """
        Устанавливает файл для загрузки. Возвращает self для поддержки цепочки.

        :param file_path: путь к файлу
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Файл не найден: {path}")

        self._file_path = path
        return self

    def with_content_type(self, content_type: str):
        self._content_type = content_type
        return self

    def with_field_name(self, field_name: str):
        self._field_name = field_name
        return self

    def build(self) -> dict[str, tuple[str, object, str]]:
        """
        Возвращает словарь, совместимый с httpx/requests: {"field_name": ("filename", file_obj, "mime/type")}
        """
        if self._file_path is None:
            raise ValueError("Файл не установлен. Вызовите .with_file(...) перед build().")
        if self._file_obj is None:
            raise RuntimeError("Используйте билдер внутри 'with' контекста.")

        # Определяем content_type только если он не был задан явно
        content_type = self._content_type
        if content_type is None:
            guessed_type, _ = mimetypes.guess_type(self._file_path)
            content_type = guessed_type or "application/octet-stream"

        filename = self._file_path.name
        return {
            self._field_name: (filename, self._file_obj, content_type)
        }

    def __enter__(self) -> 'SingleFileUploadBuilder':
        if self._file_path is None:
            raise ValueError("Файл не установлен. Вызовите .with_file(...) перед использованием в 'with'.")
        if self._file_obj is not None:
            raise RuntimeError("Этот билдер уже используется. Создайте новый экземпляр.")
        self._file_obj = self._file_path.open("rb")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._file_obj:
            self._file_obj.close()
            self._file_obj = None
