"""Appwrite Tables API client for metadata operations."""

import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from appwrite.client import Client
from appwrite.services.tables_db import TablesDB
from appwrite.query import Query
from appwrite.exception import AppwriteException

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

logger = logging.getLogger(__name__)


class AppwriteClient:
    """
    Client for interacting with Appwrite Tables API.
    
    Handles all columns from the files table schema:
    
    Required Columns:
    - fileId (string, 255): Unique file identifier (max 36 chars for rowId)
    - userId (string, 255): User ID from Appwrite authentication
    - name (string, 255): Original filename
    - size (integer): File size in bytes
    - mimeType (string, 100): MIME type of the file
    - createdAt (datetime): Creation timestamp (ISO 8601 format)
    
    Optional Columns:
    - folderId (string, 255): Optional folder ID for organization
    - description (string, 1000): Optional file description
    - tags (string array, 500): Optional list of tags
    - indexed (boolean, default: false): Whether file is indexed for semantic search
    - vectorId (string, 255): FAISS vector index identifier
    - hash (string, 64): SHA-256 hash for deduplication
    - storagePath (string, 500): S3 storage path/key
    - status (string, 50, default: "pending"): File status (pending/completed)
    """

    def __init__(self):
        """Initialize Appwrite client with configuration."""
        self.client = Client()
        self.client.set_endpoint(Config.APPWRITE_ENDPOINT)
        self.client.set_project(Config.APPWRITE_PROJECT_ID)
        self.client.set_key(Config.APPWRITE_API_KEY)
        self.tables_db = TablesDB(self.client)

    def create_file_metadata(
        self,
        file_id: str,
        user_id: str,
        name: str,
        size: int,
        mime_type: str,
        storage_path: str,
        folder_id: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new file metadata record in Appwrite Tables.
        
        All columns from the schema are handled:
        - Required: fileId, userId, name, size, mimeType, createdAt
        - Optional: folderId, description, tags, indexed, vectorId, hash, storagePath, status
        
        Args:
            file_id: Unique file identifier (required, max 36 chars)
            user_id: User ID from Appwrite authentication (required)
            name: Original filename (required, string, max 255 chars)
            size: File size in bytes (required, integer)
            mime_type: MIME type of the file (required, string, max 100 chars)
            storage_path: S3 storage path (optional, string, max 500 chars)
            folder_id: Optional folder ID (optional, string, max 255 chars)
            description: Optional file description (optional, string, max 1000 chars)
            tags: Optional list of tags (optional, string array, max 500 chars total)

        Returns:
            Created file metadata record with all columns

        Raises:
            AppwriteException: If creation fails
        """
        try:
            # Get current datetime in ISO 8601 format for createdAt field
            current_time = datetime.utcnow().isoformat() + "Z"
            
            data = {
                "fileId": file_id,
                "userId": user_id,
                "name": name,
                "size": size,
                "mimeType": mime_type,
                "storagePath": storage_path,
                "indexed": False,
                "status": "pending",
                "createdAt": current_time,  # Required by table schema
            }

            if folder_id:
                data["folderId"] = folder_id
            if description:
                data["description"] = description
            if tags:
                data["tags"] = tags

            # Validate file_id length (Appwrite requires max 36 chars)
            if len(file_id) > 36:
                raise ValueError(
                    f"File ID '{file_id}' is too long ({len(file_id)} chars). "
                    f"Appwrite rowId must be max 36 characters."
                )
            
            # Use Tables API (create_row) instead of deprecated Databases API
            result = self.tables_db.create_row(
                database_id=Config.APPWRITE_DATABASE_ID,
                table_id=Config.APPWRITE_TABLE_ID,
                row_id=file_id,
                data=data
            )

            logger.info(f"Created file metadata for {file_id}")
            # Tables API returns row object with _id, _createdAt, _updatedAt, _permissions, and data fields
            # The data field contains the actual row data
            if isinstance(result, dict):
                # Extract data from row response
                row_data = result.get("data", {})
                # Merge with metadata fields from row response
                if "_createdAt" in result:
                    row_data["createdAt"] = result["_createdAt"]
                if "_updatedAt" in result:
                    row_data["updatedAt"] = result["_updatedAt"]
                if "_id" in result:
                    row_data["_id"] = result["_id"]
                # Return the merged data
                return row_data if row_data else result
            return result

        except AppwriteException as e:
            logger.error(f"Failed to create file metadata: {e.message}")
            raise

    def get_file_metadata(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Get file metadata by ID.

        Args:
            file_id: File ID to retrieve

        Returns:
            File metadata record or None if not found
        """
        try:
            result = self.tables_db.get_row(
                database_id=Config.APPWRITE_DATABASE_ID,
                table_id=Config.APPWRITE_TABLE_ID,
                row_id=file_id
            )
            # Tables API returns row object with _id, _createdAt, _updatedAt, _permissions, and data fields
            if isinstance(result, dict):
                # Extract data from row response
                row_data = result.get("data", {})
                # Merge with metadata fields from row response
                if "_createdAt" in result:
                    row_data["createdAt"] = result["_createdAt"]
                if "_updatedAt" in result:
                    row_data["updatedAt"] = result["_updatedAt"]
                if "_id" in result:
                    row_data["_id"] = result["_id"]
                # Return the merged data
                return row_data if row_data else result
            return result
        except AppwriteException as e:
            if e.code == 404:
                return None
            logger.error(f"Failed to get file metadata: {e.message}")
            raise

    def list_files(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
        folder_id: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List files for a user with optional filtering.

        Args:
            user_id: User ID to filter by
            limit: Maximum number of results
            offset: Pagination offset
            folder_id: Optional folder ID filter
            mime_type: Optional MIME type filter

        Returns:
            Dictionary with files list and pagination info
        """
        try:
            # Build queries using Query objects
            queries = [
                Query.equal("userId", [user_id])
            ]

            if folder_id:
                queries.append(Query.equal("folderId", [folder_id]))
            if mime_type:
                queries.append(Query.equal("mimeType", [mime_type]))
            
            # Add pagination using Query objects
            queries.append(Query.limit(limit))
            queries.append(Query.offset(offset))

            result = self.tables_db.list_rows(
                Config.APPWRITE_DATABASE_ID,
                Config.APPWRITE_TABLE_ID,
                queries
            )

            # Tables API returns rows array, extract data from each row
            rows = result.get("rows", [])
            files = []
            for row in rows:
                # Extract data from row response
                row_data = row.get("data", {})
                # Merge with metadata fields from row response
                if "_createdAt" in row:
                    row_data["createdAt"] = row["_createdAt"]
                if "_updatedAt" in row:
                    row_data["updatedAt"] = row["_updatedAt"]
                if "_id" in row:
                    row_data["_id"] = row["_id"]
                # Use row_data if available, otherwise use the full row
                files.append(row_data if row_data else row)

            return {
                "files": files,
                "total": result.get("total", 0),
                "limit": limit,
                "offset": offset,
            }
        except AppwriteException as e:
            logger.error(f"Failed to list files: {e.message}")
            raise

    def update_file_metadata(
        self,
        file_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        folder_id: Optional[str] = None,
        indexed: Optional[bool] = None,
        hash: Optional[str] = None,
        status: Optional[str] = None,
        vector_id: Optional[str] = None,
        storage_path: Optional[str] = None,
        size: Optional[int] = None,
        mime_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update file metadata.

        Args:
            file_id: File ID to update
            name: Optional new name
            description: Optional new description
            tags: Optional new tags
            folder_id: Optional new folder ID
            indexed: Optional indexed status
            hash: Optional file hash
            status: Optional status
            vector_id: Optional vector ID (FAISS index identifier)
            storage_path: Optional storage path
            size: Optional file size
            mime_type: Optional MIME type

        Returns:
            Updated file metadata record
        """
        try:
            data = {}
            if name is not None:
                data["name"] = name
            if description is not None:
                data["description"] = description
            if tags is not None:
                data["tags"] = tags
            if folder_id is not None:
                data["folderId"] = folder_id
            if indexed is not None:
                data["indexed"] = indexed
            if hash is not None:
                data["hash"] = hash
            if status is not None:
                data["status"] = status
            if vector_id is not None:
                data["vectorId"] = vector_id
            if storage_path is not None:
                data["storagePath"] = storage_path
            if size is not None:
                data["size"] = size
            if mime_type is not None:
                data["mimeType"] = mime_type

            if not data:
                # No updates to make
                return self.get_file_metadata(file_id)

            result = self.tables_db.update_row(
                database_id=Config.APPWRITE_DATABASE_ID,
                table_id=Config.APPWRITE_TABLE_ID,
                row_id=file_id,
                data=data
            )

            logger.info(f"Updated file metadata for {file_id}")
            # Tables API returns row object with _id, _createdAt, _updatedAt, _permissions, and data fields
            if isinstance(result, dict):
                # Extract data from row response
                row_data = result.get("data", {})
                # Merge with metadata fields from row response
                if "_createdAt" in result:
                    row_data["createdAt"] = result["_createdAt"]
                if "_updatedAt" in result:
                    row_data["updatedAt"] = result["_updatedAt"]
                if "_id" in result:
                    row_data["_id"] = result["_id"]
                # Return the merged data
                return row_data if row_data else result
            return result

        except AppwriteException as e:
            logger.error(f"Failed to update file metadata: {e.message}")
            raise

    def delete_file_metadata(self, file_id: str) -> bool:
        """
        Delete file metadata.

        Args:
            file_id: File ID to delete

        Returns:
            True if deleted successfully
        """
        try:
            self.tables_db.delete_row(
                database_id=Config.APPWRITE_DATABASE_ID,
                table_id=Config.APPWRITE_TABLE_ID,
                row_id=file_id
            )
            logger.info(f"Deleted file metadata for {file_id}")
            return True
        except AppwriteException as e:
            if e.code == 404:
                return False
            logger.error(f"Failed to delete file metadata: {e.message}")
            raise

    def find_file_by_hash(self, hash_value: str) -> Optional[Dict[str, Any]]:
        """
        Find a file by its SHA-256 hash (for deduplication).

        Args:
            hash_value: SHA-256 hash to search for

        Returns:
            File metadata record or None if not found
        """
        try:
            queries = [
                Query.equal("hash", [hash_value]),
                Query.limit(1)
            ]
            
            result = self.tables_db.list_rows(
                Config.APPWRITE_DATABASE_ID,
                Config.APPWRITE_TABLE_ID,
                queries
            )

            rows = result.get("rows", [])
            if not rows:
                return None
            
            # Extract data from row response
            row = rows[0]
            row_data = row.get("data", {})
            # Merge with metadata fields from row response
            if "_createdAt" in row:
                row_data["createdAt"] = row["_createdAt"]
            if "_updatedAt" in row:
                row_data["updatedAt"] = row["_updatedAt"]
            if "_id" in row:
                row_data["_id"] = row["_id"]
            # Return the merged data
            return row_data if row_data else row
        except AppwriteException as e:
            logger.error(f"Failed to find file by hash: {e.message}")
            return None

