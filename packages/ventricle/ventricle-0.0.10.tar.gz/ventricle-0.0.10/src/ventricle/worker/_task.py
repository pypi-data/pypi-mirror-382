from typing import Callable, Any, Tuple, Dict, Awaitable

from pydantic import BaseModel, Field


class Task(BaseModel):
    func: Callable[..., Awaitable[Any]]
    args: Tuple[Any, ...] = Field(default_factory=tuple)
    kwargs: Dict[str, Any] = Field(default_factory=dict)