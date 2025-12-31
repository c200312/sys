"""
MinIO 对象存储服务
"""
import uuid
from io import BytesIO
from datetime import timedelta
from typing import Optional

from minio import Minio
from minio.error import S3Error

from app.core.config import get_settings


class MinioService:
    """MinIO 对象存储服务"""

    _instance: Optional["MinioService"] = None
    _client: Optional[Minio] = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            settings = get_settings()
            self._client = Minio(
                settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=settings.minio_secure
            )
            self._bucket = settings.minio_bucket
            self._ensure_bucket()

    def _ensure_bucket(self):
        """确保存储桶存在"""
        try:
            if not self._client.bucket_exists(self._bucket):
                self._client.make_bucket(self._bucket)
        except S3Error as e:
            print(f"MinIO bucket error: {e}")
            raise

    def upload_file(
        self,
        file_data: bytes,
        filename: str,
        content_type: str,
        prefix: str = "",
        folder_id: Optional[str] = None
    ) -> str:
        """
        上传文件到 MinIO

        Args:
            file_data: 文件二进制数据
            filename: 原始文件名
            content_type: MIME 类型
            prefix: 路径前缀 (如 "courses/", "homeworks/")
            folder_id: 文件夹 ID，用于组织同一文件夹的文件

        Returns:
            object_name: MinIO 中的对象名称
        """
        # 生成唯一的对象名称
        # 如果提供了 folder_id，使用它来组织文件；否则生成 UUID
        unique_id = folder_id if folder_id else str(uuid.uuid4())
        # 为避免同名文件冲突，添加短 UUID 前缀
        short_uuid = str(uuid.uuid4())[:8]
        object_name = f"{prefix}{unique_id}/{short_uuid}_{filename}"

        try:
            self._client.put_object(
                self._bucket,
                object_name,
                BytesIO(file_data),
                len(file_data),
                content_type=content_type
            )
            return object_name
        except S3Error as e:
            print(f"MinIO upload error: {e}")
            raise

    def download_file(self, object_name: str) -> bytes:
        """
        从 MinIO 下载文件

        Args:
            object_name: MinIO 中的对象名称

        Returns:
            文件二进制数据
        """
        try:
            response = self._client.get_object(self._bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            print(f"MinIO download error: {e}")
            raise

    def delete_file(self, object_name: str) -> None:
        """
        从 MinIO 删除文件

        Args:
            object_name: MinIO 中的对象名称
        """
        try:
            self._client.remove_object(self._bucket, object_name)
        except S3Error as e:
            print(f"MinIO delete error: {e}")
            raise

    def get_presigned_url(
        self,
        object_name: str,
        expires: int = 3600
    ) -> str:
        """
        获取预签名下载 URL

        Args:
            object_name: MinIO 中的对象名称
            expires: URL 有效期（秒），默认1小时

        Returns:
            预签名 URL
        """
        try:
            return self._client.presigned_get_object(
                self._bucket,
                object_name,
                expires=timedelta(seconds=expires)
            )
        except S3Error as e:
            print(f"MinIO presigned URL error: {e}")
            raise

    def file_exists(self, object_name: str) -> bool:
        """
        检查文件是否存在

        Args:
            object_name: MinIO 中的对象名称

        Returns:
            是否存在
        """
        try:
            self._client.stat_object(self._bucket, object_name)
            return True
        except S3Error:
            return False


# 全局单例
minio_service = MinioService()


def get_minio_service() -> MinioService:
    """获取 MinIO 服务实例"""
    return minio_service
