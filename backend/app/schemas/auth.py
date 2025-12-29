"""
认证相关 Schema
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ============= 请求 Schema =============

class SignupRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)
    role: str = Field(..., pattern="^(teacher|student)$")


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class PasswordChangeRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=1)


# ============= 响应 Schema =============

class UserBase(BaseModel):
    """用户基本信息"""
    id: str
    username: str
    role: str


class UserResponse(UserBase):
    """用户响应"""
    created_at: datetime


class TokenData(BaseModel):
    """Token 数据"""
    access_token: str
    token_type: str = "Bearer"
    user: UserBase


class LoginResponse(BaseModel):
    """登录响应数据"""
    access_token: str
    token_type: str = "Bearer"
    user: UserBase
