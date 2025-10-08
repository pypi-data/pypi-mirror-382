from ..config.app_config import AppConfig as AppConfig
from _typeshed import Incomplete

class UserInfo:
    user_name: Incomplete
    tenant_id: Incomplete
    tenant_enabled: Incomplete
    def __init__(self, user_name: str | None = None, tenant_id: int | None = None, tenant_enabled: bool | None = None) -> None: ...

def get_current_user_info() -> UserInfo: ...
def set_current_user_info(user_info: UserInfo): ...
