#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/9/21 下午8:47
# @Desc     ：
from typing import Optional

from pydantic import BaseModel, Field


class TenantConfigSetting(BaseModel):
    enabled: bool = Field(False, description="是否启用")
    default_id: Optional[int] = Field(None, description="默认租户ID")
    # admin_id: Optional[int] = Field(None, description="管理员租户ID")


class AuthConfigSetting(BaseModel):
    token_jwt_secret_key: str = Field(..., description="JWT TOKEN_SECRET_KEY")
    token_jwt_expire_minutes: int = Field(30, description="JWT TOKEN_ 过期时间")
    rebuild_auth_rule: bool = Field(False, description="重置")
    default_admin_roles: list[str] = ["admin"]
    default_admin_users: list[str] = ["admin"]
    tenant: TenantConfigSetting = Field(default_factory=TenantConfigSetting, description="租户")
