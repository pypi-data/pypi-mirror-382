from ..config.app_config import AppConfig as AppConfig
from ..logger.logging_ import logging as logging
from ..portal_auth.entity_table.auth_rule import AuthRule as AuthRule
from ..services.db_engine_service import DBEngineService as DBEngineService
from ..utils.core_utils import CoreUtil as CoreUtil

class PermissionEngine:
    def __new__(cls): ...
    def get_async_enforcer(self): ...
    async def check_table(self) -> None: ...
