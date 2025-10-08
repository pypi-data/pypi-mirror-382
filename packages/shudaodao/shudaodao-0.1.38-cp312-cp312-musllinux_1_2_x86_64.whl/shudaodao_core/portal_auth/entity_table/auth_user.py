#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# @License  ：(C)Copyright 2025, 数道智融科技
# @Author   ：李锋
# @Software ：PyCharm
# @Date     ：2025/9/2 下午4:24
# @Desc     ：

from datetime import datetime
from typing import Optional, Any

from pydantic import EmailStr, model_validator, computed_field
from sqlalchemy import BigInteger, Integer
from sqlmodel import SQLModel

from .. import get_schema_name, RegistryModel
from ...model.field import Field
from ...schemas.core_enum import UserStatus
from ...schemas.response import BaseResponse
from ...services.enum_service import EnumService
from ...utils.generate_unique_id import get_primary_id


class AuthUser(RegistryModel, table=True):
    """ 数据模型 - 数据库表 T_Auth_User 结构模型 """
    __tablename__ = "t_auth_user"
    __table_args__ = {"schema": f"{get_schema_name()}", "comment": "鉴权用户表"}

    user_id: Optional[int] = Field(
        default_factory=get_primary_id, primary_key=True, sa_type=BigInteger,
        sa_column_kwargs={"comment": "内码"}, description="内码")
    user_name: str = Field(
        unique=True, index=True, max_length=50, sa_column_kwargs={"comment": "内码"}, description="用户名")
    pass_word: str = Field(sa_column_kwargs={"comment": "密码"}, description="密码")
    user_email: Optional[EmailStr] = Field(
        default=None, nullable=True, max_length=100, sa_column_kwargs={"comment": "邮件"}, description="邮件")
    is_active: bool = True
    user_status: Optional[UserStatus] = Field(default=None, nullable=True, sa_type=Integer)

    last_login: Optional[datetime] = Field(default_factory=lambda: datetime.now(), description="最后登录时间")

    create_by: Optional[str] = Field(default=None, max_length=50, nullable=True, description="创建人")
    create_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(), nullable=True, description="创建日期")
    update_by: Optional[str] = Field(default=None, max_length=50, nullable=True, description="修改人")
    update_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(), nullable=True, description="修改日期")
    tenant_id: Optional[int] = Field(default=None, nullable=True, sa_type=BigInteger, description="租户内码")


class AuthUserResponse(BaseResponse):
    # user_id: Optional[int] = Field(sa_type=BigInteger)
    user_name: str = Field(max_length=50)
    user_status: Optional[UserStatus]  # ← 枚举字段
    user_email: Optional[EmailStr] = Field(default=None, max_length=100)
    is_active: Optional[bool] = Field(default=None)

    create_by: Optional[str] = Field(default=None)
    create_at: Optional[datetime] = Field(default=None)
    update_by: Optional[str] = Field(default=None)
    update_at: Optional[datetime] = Field(default=None)

    @computed_field
    @property
    def user_status_label(self) -> str:
        return self.user_status.label if self.user_status else None


class AuthLogin(SQLModel):
    """ 登录模型 """
    user_name: str = Field(min_length=3, max_length=50)
    pass_word: str = Field(min_length=6)


class AuthRegister(SQLModel):
    user_name: str = Field(min_length=5, max_length=50)
    pass_word: str = Field(min_length=5)
    user_email: Optional[EmailStr] = Field(default=None, max_length=50)

    # 输入字段：均为可选，且不设默认值
    user_status: Optional[UserStatus] = Field(default=None)
    user_status_label: Optional[str] = None
    # 注册需要租户ID
    tenant_id: Optional[int] = Field(None)

    # noinspection PyMethodParameters
    @model_validator(mode="before")
    def resolve_enums(cls, data: Any) -> Any:
        if isinstance(data, dict):
            EnumService.resolve_field(data, "user_status", UserStatus)
        return data


class AuthPassword(SQLModel):
    """ 修改密码模型 """
    old_password: str
    new_password: str = Field(min_length=6, max_length=50)
