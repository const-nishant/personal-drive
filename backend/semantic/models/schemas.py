"""Pydantic models for request/response validation."""

from typing import Optional, List
from pydantic import BaseModel, Field


# Upload Models
class PresignUploadRequest(BaseModel):
    """Request model for presigned upload URL generation."""
    name: str = Field(..., description="Original file name")
    size: int = Field(..., gt=0, description="File size in bytes")
    mimeType: str = Field(..., description="MIME type of the file")
    folderId: Optional[str] = Field(None, description="Optional folder ID")
    description: Optional[str] = Field(None, max_length=1000, description="Optional file description")
    tags: Optional[List[str]] = Field(None, description="Optional list of tags")
    uploadMode: str = Field("single", description="Upload mode: 'single' or 'multipart'")
    parts: Optional[int] = Field(None, gt=0, description="Number of parts for multipart upload")


class PresignUploadResponse(BaseModel):
    """Response model for presigned upload URL."""
    fileId: str
    upload: dict  # Contains mode, url, uploadId (if multipart), parts (if multipart)
    expiresIn: Optional[int] = None


class CompleteUploadRequest(BaseModel):
    """Request model for completing upload and indexing."""
    fileId: str = Field(..., description="File ID from presign response")


class CompleteUploadResponse(BaseModel):
    """Response model for upload completion."""
    status: str
    fileId: str
    hash: Optional[str] = None
    textExtracted: bool = False
    indexed: bool = False


# File Management Models
class FileMetadata(BaseModel):
    """File metadata model."""
    fileId: str
    name: str
    size: int
    mimeType: str
    hash: Optional[str] = None
    storagePath: str
    createdAt: str
    userId: str
    folderId: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    indexed: bool = False
    status: str = "pending"


class ListFilesResponse(BaseModel):
    """Response model for file listing."""
    files: List[FileMetadata]
    total: int
    limit: int
    offset: int


class UpdateFileRequest(BaseModel):
    """Request model for updating file metadata."""
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = None
    folderId: Optional[str] = None


class UpdateFileResponse(BaseModel):
    """Response model for file update."""
    status: str
    file: FileMetadata


class DeleteFileResponse(BaseModel):
    """Response model for file deletion."""
    status: str
    fileId: str


class DownloadUrlResponse(BaseModel):
    """Response model for download URL generation."""
    url: str
    expiresIn: int
    fileId: str


# Search Models
class SearchRequest(BaseModel):
    """Request model for semantic search."""
    query: str = Field(..., min_length=1, max_length=500, description="Search query")
    k: int = Field(5, gt=0, le=100, description="Number of results to return")
    folderId: Optional[str] = Field(None, description="Optional folder ID filter")


class SearchResult(BaseModel):
    """Individual search result model."""
    fileId: str
    name: str
    score: float
    size: int
    mimeType: str
    createdAt: str
    description: Optional[str] = None


class SearchResponse(BaseModel):
    """Response model for search."""
    results: List[SearchResult]
    query: str
    total: int


# System Models
class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    model_loaded: bool
    index_initialized: bool
    index_size: int
    documents_indexed: int


class StatsResponse(BaseModel):
    """Response model for service statistics."""
    model: str
    embedding_dimension: int
    index_size: int
    documents_indexed: int
    index_path: str
    meta_path: str


class APIInfoResponse(BaseModel):
    """Response model for API information."""
    service: str
    status: str
    endpoints: dict
    docs: str

