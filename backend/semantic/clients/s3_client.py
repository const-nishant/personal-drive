"""S3 client for presigned URL generation and file operations."""

import logging
from datetime import timedelta
from typing import Optional, List, Dict, Any
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config as BotoConfig

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

logger = logging.getLogger(__name__)


class S3Client:
    """Client for S3-compatible storage operations."""

    def __init__(self):
        """Initialize S3 client with configuration."""
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=Config.S3_ENDPOINT,
            aws_access_key_id=Config.S3_ACCESS_KEY_ID,
            aws_secret_access_key=Config.S3_SECRET_ACCESS_KEY,
            region_name=Config.S3_REGION,
            config=BotoConfig(signature_version="s3v4")
        )
        self.bucket_name = Config.S3_BUCKET_NAME

    def generate_presigned_upload_url(
        self,
        key: str,
        mime_type: str,
        expires_in: int = None,
    ) -> str:
        """
        Generate a presigned URL for file upload.

        Args:
            key: S3 object key (storage path)
            mime_type: MIME type of the file
            expires_in: URL expiration time in seconds (default: 15 minutes)

        Returns:
            Presigned upload URL
        """
        if expires_in is None:
            expires_in = Config.PRESIGNED_UPLOAD_EXPIRES_IN

        try:
            url = self.s3_client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                    "ContentType": mime_type,
                },
                ExpiresIn=expires_in,
            )
            logger.info(f"Generated presigned upload URL for {key}")
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned upload URL: {e}")
            raise

    def generate_presigned_download_url(
        self,
        key: str,
        expires_in: int = None,
    ) -> str:
        """
        Generate a presigned URL for file download.

        Args:
            key: S3 object key (storage path)
            expires_in: URL expiration time in seconds (default: 1 hour)

        Returns:
            Presigned download URL
        """
        if expires_in is None:
            expires_in = Config.PRESIGNED_DOWNLOAD_EXPIRES_IN

        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": key,
                },
                ExpiresIn=expires_in,
            )
            logger.info(f"Generated presigned download URL for {key}")
            return url
        except ClientError as e:
            logger.error(f"Failed to generate presigned download URL: {e}")
            raise

    def generate_multipart_upload_urls(
        self,
        key: str,
        mime_type: str,
        parts: int,
        expires_in: int = None,
    ) -> Dict[str, Any]:
        """
        Generate presigned URLs for multipart upload.

        Args:
            key: S3 object key (storage path)
            mime_type: MIME type of the file
            parts: Number of parts for multipart upload
            expires_in: URL expiration time in seconds (default: 15 minutes)

        Returns:
            Dictionary with uploadId and list of presigned URLs for each part
        """
        if expires_in is None:
            expires_in = Config.PRESIGNED_UPLOAD_EXPIRES_IN

        try:
            # Create multipart upload
            response = self.s3_client.create_multipart_upload(
                Bucket=self.bucket_name,
                Key=key,
                ContentType=mime_type,
            )
            upload_id = response["UploadId"]

            # Generate presigned URLs for each part
            part_urls = []
            for part_number in range(1, parts + 1):
                url = self.s3_client.generate_presigned_url(
                    "upload_part",
                    Params={
                        "Bucket": self.bucket_name,
                        "Key": key,
                        "UploadId": upload_id,
                        "PartNumber": part_number,
                    },
                    ExpiresIn=expires_in,
                )
                part_urls.append({
                    "partNumber": part_number,
                    "url": url,
                })

            logger.info(f"Generated multipart upload URLs for {key} ({parts} parts)")
            return {
                "uploadId": upload_id,
                "parts": part_urls,
            }
        except ClientError as e:
            logger.error(f"Failed to generate multipart upload URLs: {e}")
            raise

    def download_file(self, key: str) -> bytes:
        """
        Download a file from S3.

        Args:
            key: S3 object key (storage path)

        Returns:
            File content as bytes
        """
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            content = response["Body"].read()
            logger.info(f"Downloaded file {key} ({len(content)} bytes)")
            return content
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                logger.error(f"File not found: {key}")
                raise FileNotFoundError(f"File not found: {key}")
            logger.error(f"Failed to download file: {e}")
            raise

    def delete_file(self, key: str) -> bool:
        """
        Delete a file from S3.

        Args:
            key: S3 object key (storage path)

        Returns:
            True if deleted successfully
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            logger.info(f"Deleted file {key}")
            return True
        except ClientError as e:
            logger.error(f"Failed to delete file: {e}")
            raise

    def file_exists(self, key: str) -> bool:
        """
        Check if a file exists in S3.

        Args:
            key: S3 object key (storage path)

        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=key,
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            logger.error(f"Failed to check file existence: {e}")
            raise

