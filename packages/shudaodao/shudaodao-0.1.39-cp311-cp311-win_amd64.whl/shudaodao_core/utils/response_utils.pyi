from ..config.app_config import AppConfig as AppConfig
from ..schemas.response import DataResponse as DataResponse, ErrorResponse as ErrorResponse
from fastapi.responses import Response as Response
from typing import Any

class ResponseUtil:
    @classmethod
    def success(cls, *, message: str = '操作成功', data: Any | None = None, name: str | None = None) -> Response: ...
    @classmethod
    def failure(cls, *, message: str = '操作失败', code: int = 500, data: Any | None = None, name: str | None = None) -> Response: ...
    @classmethod
    def error(cls, *, error: Any | None, message: str = '服务器异常', code: int = 500, name: str | None = None) -> Response: ...
