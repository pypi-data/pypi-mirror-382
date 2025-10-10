from collections.abc import Callable
from enum import Enum
from typing import TypeVar

from pydantic import BaseModel


E = TypeVar("E", bound=Enum)

def validate_enum_subset(base_enum: type[Enum]) -> Callable[[type[E]], type[E]]:
    def decorator(cls: type[E]) -> type[E]:
        base_values = {field.value for field in base_enum}
        cls_values = {field.value for field in cls}

        missing_in_base = cls_values - base_values
        if missing_in_base:
            raise ValueError(
                f"Поля {missing_in_base} в {cls.__name__} отсутствуют в базовом {base_enum.__name__}"
            )
        return cls
    return decorator


M = TypeVar("M", bound=BaseModel)

def validate_model_subset(base_model: type[BaseModel]) -> Callable[[type[M]], type[M]]:
    def decorator(cls: type[M]) -> type[M]:
        base_fields = set(base_model.model_fields.keys())
        cls_fields = set(cls.model_fields.keys())

        missing_in_base = cls_fields - base_fields
        if missing_in_base:
            raise ValueError(
                f"Поля {missing_in_base} в {cls.__name__} отсутствуют в базовой модели {base_model.__name__}"
            )
        return cls
    return decorator