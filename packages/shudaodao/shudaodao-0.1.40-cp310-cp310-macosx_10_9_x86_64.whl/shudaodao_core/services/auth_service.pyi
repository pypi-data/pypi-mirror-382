from ..config.app_config import AppConfig as AppConfig
from ..exception.service_exception import AuthException as AuthException, LoginException as LoginException
from ..logger.logging_ import logging as logging
from ..portal_auth.entity_table.auth_user import AuthLogin as AuthLogin, AuthPassword as AuthPassword, AuthUser as AuthUser, AuthUserResponse as AuthUserResponse
from ..services.data_service import DataService as DataService
from ..services.db_engine_service import DBEngineService as DBEngineService
from ..tools.tenant_checker import TenantManager as TenantManager
from .casbin_service import PermissionService as PermissionService
from _typeshed import Incomplete
from datetime import timedelta
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncSession

class AuthService:
    TOKEN_SECRET_KEY: Incomplete
    TOKEN_ALGORITHM: str
    TOKEN_EXPIRE_MINUTES: Incomplete
    oauth2_scheme: Incomplete
    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool: ...
    @classmethod
    def hash_password(cls, password: str) -> str: ...
    @classmethod
    def token_encode(cls, data: dict, expires_delta: timedelta | None = None) -> str: ...
    @classmethod
    def token_decode(cls, token) -> dict: ...
    @classmethod
    def get_permission(cls): ...
    @classmethod
    async def get_current_user(cls, token=..., db: AsyncSession = ...) -> AuthUserResponse: ...
    @classmethod
    async def logout(cls) -> None: ...
    @classmethod
    async def refresh(cls) -> None: ...
    @classmethod
    async def login(cls, *, db: AsyncSession, auth_login: AuthLogin): ...
    @classmethod
    async def modify_password(cls, db: AsyncSession, *, password_model: AuthPassword, current_user: AuthUserResponse): ...
