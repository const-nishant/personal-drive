"""FastAPI application for Personal Drive Python Service."""

import logging
from typing import Annotated
from fastapi import FastAPI, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse

# Import configuration and authentication
from config import Config
from auth import verify_api_key, get_user_id

# Import services
from services.file_service import FileService
from services.semantic_indexer import SemanticIndexer

# Import models
from models.schemas import (
    PresignUploadRequest,
    PresignUploadResponse,
    CompleteUploadRequest,
    CompleteUploadResponse,
    ListFilesResponse,
    FileMetadata,
    UpdateFileRequest,
    UpdateFileResponse,
    DeleteFileResponse,
    DownloadUrlResponse,
    SearchRequest,
    SearchResponse,
    HealthResponse,
    StatsResponse,
    APIInfoResponse,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Personal Drive Python Service",
    description="Unified backend service for file management and semantic search",
    version="1.0.0"
)

# Initialize services (will be initialized on startup)
file_service: FileService = None
semantic_indexer: SemanticIndexer = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global file_service, semantic_indexer

    # Validate configuration
    if not Config.validate():
        logger.error("Configuration validation failed. Please check environment variables.")
        raise RuntimeError("Configuration validation failed")

    logger.info("Initializing services...")
    file_service = FileService()
    semantic_indexer = SemanticIndexer()
    logger.info("Services initialized successfully")


# ==================== System Endpoints ====================

@app.get("/", response_model=APIInfoResponse)
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Personal Drive Python Service",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "stats": "/stats",
            "upload": {
                "presign": "/api/v1/upload/presign",
                "complete": "/api/v1/upload/complete"
            },
            "files": {
                "list": "/api/v1/files",
                "get": "/api/v1/files/{file_id}",
                "update": "/api/v1/files/{file_id}",
                "delete": "/api/v1/files/{file_id}",
                "download": "/api/v1/files/{file_id}/download"
            },
            "search": "/api/v1/search"
        },
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    stats = semantic_indexer.get_stats()
    return {
        "status": "ok",
        "model_loaded": semantic_indexer.model is not None,
        "index_initialized": semantic_indexer.index is not None,
        "index_size": stats["index_size"],
        "documents_indexed": stats["documents_indexed"],
    }


@app.get("/stats", response_model=StatsResponse)
async def get_stats(api_key: Annotated[str, Depends(verify_api_key)]):
    """Get service statistics."""
    stats = semantic_indexer.get_stats()
    return {
        "model": stats["model"],
        "embedding_dimension": stats["embedding_dimension"],
        "index_size": stats["index_size"],
        "documents_indexed": stats["documents_indexed"],
        "index_path": Config.get_index_path(),
        "meta_path": Config.get_meta_path(),
    }


# ==================== File Upload Endpoints ====================

@app.post("/api/v1/upload/presign", response_model=PresignUploadResponse)
async def presign_upload(
    request: PresignUploadRequest,
    api_key: Annotated[str, Depends(verify_api_key)],
    user_id: Annotated[str, Depends(get_user_id)],
):
    """Generate presigned URL for file upload."""
    try:
        result = file_service.presign_upload(
            user_id=user_id,
            name=request.name,
            size=request.size,
            mime_type=request.mimeType,
            folder_id=request.folderId,
            description=request.description,
            tags=request.tags,
            upload_mode=request.uploadMode,
            parts=request.parts,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate presigned URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate presigned URL"
        )


@app.post("/api/v1/upload/complete", response_model=CompleteUploadResponse)
async def complete_upload(
    request: CompleteUploadRequest,
    api_key: Annotated[str, Depends(verify_api_key)],
    user_id: Annotated[str, Depends(get_user_id)],
):
    """Complete file upload, extract text, and index."""
    try:
        result = file_service.complete_upload(
            user_id=user_id,
            file_id=request.fileId,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to complete upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete upload"
        )


# ==================== File Management Endpoints ====================

@app.get("/api/v1/files", response_model=ListFilesResponse)
async def list_files(
    api_key: Annotated[str, Depends(verify_api_key)],
    user_id: Annotated[str, Depends(get_user_id)],
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    folderId: str = Query(None),
    mimeType: str = Query(None),
):
    """List user's files with pagination."""
    try:
        result = file_service.list_files(
            user_id=user_id,
            limit=limit,
            offset=offset,
            folder_id=folderId,
            mime_type=mimeType,
        )
        return result
    except Exception as e:
        logger.error(f"Failed to list files: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list files"
        )


@app.get("/api/v1/files/{file_id}", response_model=FileMetadata)
async def get_file(
    file_id: str,
    api_key: Annotated[str, Depends(verify_api_key)],
    user_id: Annotated[str, Depends(get_user_id)],
):
    """Get file metadata by ID."""
    try:
        result = file_service.get_file(user_id=user_id, file_id=file_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get file"
        )


@app.put("/api/v1/files/{file_id}", response_model=UpdateFileResponse)
async def update_file(
    file_id: str,
    request: UpdateFileRequest,
    api_key: Annotated[str, Depends(verify_api_key)],
    user_id: Annotated[str, Depends(get_user_id)],
):
    """Update file metadata."""
    try:
        result = file_service.update_file(
            user_id=user_id,
            file_id=file_id,
            name=request.name,
            description=request.description,
            tags=request.tags,
            folder_id=request.folderId,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update file"
        )


@app.delete("/api/v1/files/{file_id}", response_model=DeleteFileResponse)
async def delete_file(
    file_id: str,
    api_key: Annotated[str, Depends(verify_api_key)],
    user_id: Annotated[str, Depends(get_user_id)],
):
    """Delete a file and its metadata."""
    try:
        result = file_service.delete_file(user_id=user_id, file_id=file_id)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete file"
        )


@app.get("/api/v1/files/{file_id}/download", response_model=DownloadUrlResponse)
async def get_download_url(
    file_id: str,
    api_key: Annotated[str, Depends(verify_api_key)],
    user_id: Annotated[str, Depends(get_user_id)],
    expiresIn: int = Query(None, ge=60, le=86400),
):
    """Get presigned download URL for a file."""
    try:
        result = file_service.get_download_url(
            user_id=user_id,
            file_id=file_id,
            expires_in=expiresIn,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get download URL: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get download URL"
        )


# ==================== Search Endpoint ====================

@app.post("/api/v1/search", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    api_key: Annotated[str, Depends(verify_api_key)],
    user_id: Annotated[str, Depends(get_user_id)],
):
    """Perform semantic search across user's files."""
    try:
        result = file_service.search_files(
            user_id=user_id,
            query=request.query,
            k=request.k,
            folder_id=request.folderId,
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
