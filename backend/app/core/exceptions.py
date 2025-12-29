"""
异常定义模块
自定义业务异常
"""
from typing import Optional


class AppException(Exception):
    """应用基础异常"""

    def __init__(
        self,
        message: str,
        code: str = "SYS_001",
        status_code: int = 500
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class AuthenticationError(AppException):
    """认证错误"""

    def __init__(self, message: str = "用户名或密码错误", code: str = "AUTH_001"):
        super().__init__(message=message, code=code, status_code=401)


class TokenError(AppException):
    """Token 错误"""

    def __init__(self, message: str = "Token无效或已过期", code: str = "AUTH_002"):
        super().__init__(message=message, code=code, status_code=401)


class UserExistsError(AppException):
    """用户已存在"""

    def __init__(self, message: str = "用户名已存在", code: str = "AUTH_003"):
        super().__init__(message=message, code=code, status_code=409)


class PermissionDeniedError(AppException):
    """权限拒绝"""

    def __init__(self, message: str = "无权限访问", code: str = "AUTH_004"):
        super().__init__(message=message, code=code, status_code=403)


class ValidationError(AppException):
    """验证错误"""

    def __init__(self, message: str, code: str = "VALID_001"):
        super().__init__(message=message, code=code, status_code=400)


class NotFoundError(AppException):
    """资源不存在"""

    def __init__(self, message: str = "资源不存在", code: str = "RES_001"):
        super().__init__(message=message, code=code, status_code=404)


class ConflictError(AppException):
    """资源冲突"""

    def __init__(self, message: str = "资源冲突", code: str = "RES_003"):
        super().__init__(message=message, code=code, status_code=409)


class DatabaseError(AppException):
    """数据库错误"""

    def __init__(self, message: str = "数据库操作失败", code: str = "SYS_002"):
        super().__init__(message=message, code=code, status_code=500)
