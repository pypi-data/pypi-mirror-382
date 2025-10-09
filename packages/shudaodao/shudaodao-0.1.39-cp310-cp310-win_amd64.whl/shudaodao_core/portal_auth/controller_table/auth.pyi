from .. import get_engine_name as get_engine_name
from ...auth.auth_router import AuthRouter as AuthRouter
from ...config.app_config import AppConfig as AppConfig
from ...exception.service_exception import ServiceErrorException as ServiceErrorException
from ...services.auth_service import AuthService as AuthService
from ...services.data_service import DataService as DataService
from ...tools.tenant_checker import TenantManager as TenantManager
from ...utils.response_utils import ResponseUtil as ResponseUtil
from ..entity_table.auth_user import AuthLogin as AuthLogin, AuthPassword as AuthPassword, AuthRegister as AuthRegister, AuthUser as AuthUser, AuthUserResponse as AuthUserResponse
from _typeshed import Incomplete
from fastapi import Request as Request
from fastapi.security import OAuth2PasswordRequestForm as OAuth2PasswordRequestForm
from sqlalchemy import literal as literal
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncSession

Auth_Controller: Incomplete

async def auth_register(register_model: AuthRegister, db: AsyncSession = ...): ...
async def auth_login(login_model: AuthLogin, db: AsyncSession = ...): ...
async def auth_token(request: Request, form_data: OAuth2PasswordRequestForm = ..., db: AsyncSession = ...): ...
async def auth_logout(): ...
async def auth_refresh(): ...
async def auth_me(current_user: AuthUserResponse = ...): ...
async def auth_me_password(password_model: AuthPassword, db: AsyncSession = ..., current_user: AuthUserResponse = ...): ...
