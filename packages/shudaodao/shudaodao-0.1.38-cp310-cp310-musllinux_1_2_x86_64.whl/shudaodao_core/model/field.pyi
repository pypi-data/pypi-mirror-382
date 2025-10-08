from sqlmodel import Field as SQLModelField
from typing import Any

def Field(*args: Any, **kwargs: Any) -> SQLModelField: ...
