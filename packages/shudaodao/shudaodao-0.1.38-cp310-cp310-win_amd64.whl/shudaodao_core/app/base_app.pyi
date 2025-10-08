import abc
from ..auth.auth_router import AuthRouter as AuthRouter
from ..config.app_config import AppConfig as AppConfig
from ..config.schemas.routers import RouterConfigSetting as RouterConfigSetting
from ..license.verify import verify_license as verify_license
from ..logger.logging_ import logging as logging
from ..portal_auth import auth_registry as auth_registry
from ..portal_auth.entity_table.auth_user import AuthRegister as AuthRegister, AuthUser as AuthUser
from ..services.auth_service import AuthService as AuthService
from ..services.casbin_service import PermissionService as PermissionService
from ..services.data_service import DataService as DataService
from ..services.db_engine_service import DBEngineService as DBEngineService
from ..tools.class_scaner import ClassScanner as ClassScanner
from ..tools.database_checker import DatabaseChecker as DatabaseChecker
from ..tools.tenant_checker import TenantManager as TenantManager
from ..utils.core_utils import CoreUtil as CoreUtil
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from fastapi import FastAPI

class BaseApplication(ABC, metaclass=abc.ABCMeta):
    app: Incomplete
    def __init__(self) -> None: ...
    @abstractmethod
    def application_init(self, app: FastAPI) -> None: ...
    @abstractmethod
    async def application_load(self): ...
    @abstractmethod
    async def application_unload(self): ...
