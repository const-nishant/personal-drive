"""File service for orchestrating file operations."""

import logging
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clients.appwrite_client import AppwriteClient
from clients.s3_client import S3Client
from services.text_extractor import TextExtractor
from services.semantic_indexer import SemanticIndexer
from utils.validators import (
    validate_file_name,
    validate_file_size,
    validate_mime_type,
    validate_file_id,
    sanitize_path
)
from config import Config

logger = logging.getLogger(__name__)


class FileService:
    """Service for managing file operations."""

    def __init__(self):
        """Initialize file service with dependencies."""
        self.appwrite_client = AppwriteClient()
        self.s3_client = S3Client()
        self.text_extractor = TextExtractor()
        self.semantic_indexer = SemanticIndexer()

    def generate_storage_path(
        self,
        file_id: str,
        file_name: str,
        mime_type: str,
        user_id: str
    ) -> str:
        """
        Generate storage path for a file.

        Args:
            file_id: Unique file identifier
            file_name: Original file name
            mime_type: MIME type of the file
            user_id: User ID

        Returns:
            Storage path (S3 key)
        """
        sanitized_name = validate_file_name(file_name)
        now = datetime.now()
        year = now.year
        month = f"{now.month:02d}"

        if mime_type.startswith("image/"):
            return f"photos/{year}/{month}/{file_id}_{sanitized_name}"
        else:
            return f"documents/{user_id}/{file_id}_{sanitized_name}"

    def presign_upload(
        self,
        user_id: str,
        name: str,
        size: int,
        mime_type: str,
        folder_id: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        upload_mode: str = "single",
        parts: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Generate presigned upload URL and create file metadata.

        Args:
            user_id: User ID from authentication
            name: File name
            size: File size in bytes
            mime_type: MIME type
            folder_id: Optional folder ID
            description: Optional description
            tags: Optional tags
            upload_mode: Upload mode ('single' or 'multipart')
            parts: Number of parts for multipart upload

        Returns:
            Dictionary with fileId and upload information
        """
        # Validate inputs
        sanitized_name = validate_file_name(name)
        validated_size = validate_file_size(size)
        validated_mime = validate_mime_type(mime_type)

        # Generate file ID (max 36 chars for Appwrite documentId)
        # Using 24 bytes = 32 chars base64, which fits within Appwrite's 36 char limit
        # Ensure it starts with alphanumeric (Appwrite requirement)
        import secrets
        import string
        
        # Generate random ID and ensure it starts with alphanumeric
        file_id = secrets.token_urlsafe(24)
        # If it starts with a special char, prepend a random alphanumeric
        if file_id[0] not in (string.ascii_letters + string.digits):
            file_id = secrets.choice(string.ascii_letters + string.digits) + file_id
            # Truncate to 36 chars if needed
            file_id = file_id[:36]

        # Generate storage path
        storage_path = self.generate_storage_path(
            file_id, sanitized_name, validated_mime, user_id
        )

        # Create file metadata in Appwrite
        try:
            self.appwrite_client.create_file_metadata(
                file_id=file_id,
                user_id=user_id,
                name=sanitized_name,
                size=validated_size,
                mime_type=validated_mime,
                storage_path=storage_path,
                folder_id=folder_id,
                description=description,
                tags=tags,
            )
        except Exception as e:
            logger.error(f"Failed to create file metadata: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create file metadata"
            )

        # Generate presigned URL(s)
        try:
            if upload_mode == "multipart" and parts:
                multipart_info = self.s3_client.generate_multipart_upload_urls(
                    key=storage_path,
                    mime_type=validated_mime,
                    parts=parts,
                )
                return {
                    "fileId": file_id,
                    "upload": {
                        "mode": "multipart",
                        "uploadId": multipart_info["uploadId"],
                        "parts": multipart_info["parts"],
                    },
                    "expiresIn": Config.PRESIGNED_UPLOAD_EXPIRES_IN,
                }
            else:
                url = self.s3_client.generate_presigned_upload_url(
                    key=storage_path,
                    mime_type=validated_mime,
                )
                return {
                    "fileId": file_id,
                    "upload": {
                        "mode": "single",
                        "url": url,
                    },
                    "expiresIn": Config.PRESIGNED_UPLOAD_EXPIRES_IN,
                }
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            # Clean up metadata if URL generation fails
            try:
                self.appwrite_client.delete_file_metadata(file_id)
            except:
                pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate presigned URL"
            )

    def complete_upload(
        self,
        user_id: str,
        file_id: str,
    ) -> Dict[str, Any]:
        """
        Complete file upload: download, extract text, compute hash, and index.

        Args:
            user_id: User ID from authentication
            file_id: File ID from presign response

        Returns:
            Dictionary with completion status
        """
        # Validate file ID
        validated_file_id = validate_file_id(file_id)

        # Get file metadata
        metadata = self.appwrite_client.get_file_metadata(validated_file_id)
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        # Verify ownership
        if metadata.get("userId") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="File belongs to different user"
            )

        storage_path = metadata.get("storagePath")
        mime_type = metadata.get("mimeType")

        # Download file from S3
        try:
            file_content = self.s3_client.download_file(storage_path)
        except FileNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found in storage"
            )
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to download file from storage"
            )

        # Compute SHA-256 hash
        file_hash = hashlib.sha256(file_content).hexdigest()

        # Check for deduplication
        existing_file = self.appwrite_client.find_file_by_hash(file_hash)
        if existing_file and existing_file.get("fileId") != validated_file_id:
            logger.info(f"File with hash {file_hash} already exists, reusing storage")
            # Update metadata to point to existing file
            storage_path = existing_file.get("storagePath")

        # Extract text
        text_extracted = False
        extracted_text = None
        if self.text_extractor.is_supported(mime_type):
            extracted_text = self.text_extractor.extract_text(file_content, mime_type)
            text_extracted = extracted_text is not None

        # Index semantically
        indexed = False
        vector_id = None
        if extracted_text:
            try:
                vector_id = self.semantic_indexer.index_document(validated_file_id, extracted_text)
                indexed = vector_id is not None
            except Exception as e:
                logger.error(f"Failed to index document: {e}")

        # Update metadata with all fields
        try:
            self.appwrite_client.update_file_metadata(
                file_id=validated_file_id,
                hash=file_hash,
                indexed=indexed,
                status="completed",
                vector_id=str(vector_id) if vector_id is not None else None,
            )
        except Exception as e:
            logger.error(f"Failed to update metadata: {e}")

        return {
            "status": "indexed" if indexed else "completed",
            "fileId": validated_file_id,
            "hash": file_hash,
            "textExtracted": text_extracted,
            "indexed": indexed,
            "vectorId": str(vector_id) if vector_id is not None else None,
        }

    def list_files(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        folder_id: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List user's files.

        Args:
            user_id: User ID
            limit: Maximum number of results
            offset: Pagination offset
            folder_id: Optional folder filter
            mime_type: Optional MIME type filter

        Returns:
            Dictionary with files list and pagination info
        """
        return self.appwrite_client.list_files(
            user_id=user_id,
            limit=limit,
            offset=offset,
            folder_id=folder_id,
            mime_type=mime_type,
        )

    def get_file(self, user_id: str, file_id: str) -> Dict[str, Any]:
        """
        Get file metadata.

        Args:
            user_id: User ID
            file_id: File ID

        Returns:
            File metadata

        Raises:
            HTTPException: If file not found or access denied
        """
        metadata = self.appwrite_client.get_file_metadata(file_id)
        if not metadata:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )

        if metadata.get("userId") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="File belongs to different user"
            )

        return metadata

    def update_file(
        self,
        user_id: str,
        file_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update file metadata.

        Args:
            user_id: User ID
            file_id: File ID
            name: Optional new name
            description: Optional new description
            tags: Optional new tags
            folder_id: Optional new folder ID

        Returns:
            Updated file metadata
        """
        # Verify ownership
        metadata = self.get_file(user_id, file_id)

        # Update metadata
        updated = self.appwrite_client.update_file_metadata(
            file_id=file_id,
            name=validate_file_name(name) if name else None,
            description=description,
            tags=tags,
            folder_id=folder_id,
        )

        return {
            "status": "updated",
            "file": updated,
        }

    def delete_file(self, user_id: str, file_id: str) -> Dict[str, Any]:
        """
        Delete a file and its metadata.

        Args:
            user_id: User ID
            file_id: File ID

        Returns:
            Deletion status
        """
        # Verify ownership
        metadata = self.get_file(user_id, file_id)

        storage_path = metadata.get("storagePath")

        # Delete from S3
        try:
            self.s3_client.delete_file(storage_path)
        except Exception as e:
            logger.error(f"Failed to delete file from S3: {e}")

        # Remove from semantic index
        try:
            self.semantic_indexer.remove_document(file_id)
        except Exception as e:
            logger.error(f"Failed to remove from index: {e}")

        # Delete metadata
        self.appwrite_client.delete_file_metadata(file_id)

        return {
            "status": "deleted",
            "fileId": file_id,
        }

    def get_download_url(
        self,
        user_id: str,
        file_id: str,
        expires_in: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get presigned download URL.

        Args:
            user_id: User ID
            file_id: File ID
            expires_in: Optional expiration time in seconds

        Returns:
            Dictionary with download URL and expiration
        """
        # Verify ownership
        metadata = self.get_file(user_id, file_id)

        storage_path = metadata.get("storagePath")

        if expires_in:
            expires_in = min(expires_in, 86400)  # Max 24 hours

        url = self.s3_client.generate_presigned_download_url(
            key=storage_path,
            expires_in=expires_in,
        )

        return {
            "url": url,
            "expiresIn": expires_in or Config.PRESIGNED_DOWNLOAD_EXPIRES_IN,
            "fileId": file_id,
        }

    def search_files(
        self,
        user_id: str,
        query: str,
        k: int = 5,
        folder_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform semantic search across user's files.

        Args:
            user_id: User ID
            query: Search query
            k: Number of results
            folder_id: Optional folder filter

        Returns:
            Search results with file metadata
        """
        # Perform semantic search
        file_ids = self.semantic_indexer.search(query, k)

        if not file_ids:
            return {
                "results": [],
                "query": query,
                "total": 0,
            }

        # Get metadata for all results
        results = []
        for file_id in file_ids:
            metadata = self.appwrite_client.get_file_metadata(file_id)
            if not metadata:
                continue

            # Filter by user and folder
            if metadata.get("userId") != user_id:
                continue

            if folder_id and metadata.get("folderId") != folder_id:
                continue

            # Calculate score (simplified - in production, get from FAISS)
            results.append({
                "fileId": metadata.get("fileId"),
                "name": metadata.get("name"),
                "score": 0.95,  # Placeholder - should get from FAISS search
                "size": metadata.get("size"),
                "mimeType": metadata.get("mimeType"),
                "createdAt": metadata.get("createdAt"),
                "description": metadata.get("description"),
            })

        return {
            "results": results,
            "query": query,
            "total": len(results),
        }

