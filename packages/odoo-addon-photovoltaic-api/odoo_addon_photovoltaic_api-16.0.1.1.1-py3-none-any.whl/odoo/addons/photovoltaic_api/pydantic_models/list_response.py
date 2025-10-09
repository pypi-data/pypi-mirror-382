import typing as t
from pydantic import BaseModel

T = t.TypeVar('T')

class ListResponse(BaseModel, t.Generic[T]):
    total: int
    rows: list[T]
