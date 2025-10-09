from _typeshed import Incomplete
from typing import Any

def raise_request_validation_error(*, loc_type: str, msg: str): ...
def raise_permission_exception(*, message: str, errors: str = None): ...

class ShudaodaoException(Exception):
    code: Incomplete
    name: Incomplete
    errors: Incomplete
    message: Incomplete
    def __init__(self, code: int, name: str, message: str, errors: Any = None) -> None: ...

class LoginException(ShudaodaoException):
    def __init__(self, *, message: str, errors: str = None) -> None: ...

class AuthException(ShudaodaoException):
    def __init__(self, *, message: str, errors: str = None) -> None: ...

class PermissionException(ShudaodaoException):
    def __init__(self, *, message: str, errors: str = None) -> None: ...

class ServiceErrorException(ShudaodaoException):
    def __init__(self, *, message: str, errors: str = None) -> None: ...

class DataNotFoundException(ShudaodaoException):
    def __init__(self, *, message: str = '数据未找到', model_class: str | None = None, primary_id: int | None = None, primary_field: str | list[str] | None = None) -> None: ...
