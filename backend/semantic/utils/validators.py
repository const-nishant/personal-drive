"""Input validation and sanitization utilities."""

import re
import logging
from typing import Optional
from fastapi import HTTPException, status

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

logger = logging.getLogger(__name__)


def validate_file_name(name: str) -> str:
    """
    Validate and sanitize file name.

    Args:
        name: Original file name

    Returns:
        Sanitized file name

    Raises:
        HTTPException: If file name is invalid
    """
    if not name or not name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File name is required"
        )

    # Sanitize file name (remove path traversal attempts, special characters)
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', name)
    sanitized = sanitized[:255]  # Limit length

    if not sanitized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file name"
        )

    return sanitized


def validate_file_size(size: int) -> int:
    """
    Validate file size.

    Args:
        size: File size in bytes

    Returns:
        Validated file size

    Raises:
        HTTPException: If file size is invalid or too large
    """
    if not isinstance(size, int) or size <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be a positive integer"
        )

    if size > Config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum allowed size ({Config.MAX_FILE_SIZE} bytes)"
        )

    return size


def validate_mime_type(mime_type: str) -> str:
    """
    Validate MIME type against whitelist.

    Args:
        mime_type: MIME type to validate

    Returns:
        Validated MIME type

    Raises:
        HTTPException: If MIME type is not allowed
    """
    if not mime_type or not mime_type.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MIME type is required"
        )

    if mime_type not in Config.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"MIME type '{mime_type}' is not allowed. Allowed types: {', '.join(Config.ALLOWED_MIME_TYPES)}"
        )

    return mime_type


def validate_file_id(file_id: str) -> str:
    """
    Validate file ID format for Appwrite compatibility.

    Appwrite documentId requirements:
    - Max 36 characters
    - Valid chars: a-z, A-Z, 0-9, period, hyphen, underscore
    - Can't start with a special character

    Args:
        file_id: File ID to validate

    Returns:
        Validated file ID

    Raises:
        HTTPException: If file ID is invalid
    """
    if not file_id or not file_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File ID is required"
        )

    file_id = file_id.strip()

    # Check length (Appwrite max is 36 chars)
    if len(file_id) > 36:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File ID is too long ({len(file_id)} chars). Maximum is 36 characters."
        )

    # File ID should be alphanumeric with periods, hyphens, and underscores
    # Valid chars: a-z, A-Z, 0-9, period, hyphen, underscore
    if not re.match(r'^[a-zA-Z0-9._-]+$', file_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file ID format. Only alphanumeric characters, periods, hyphens, and underscores are allowed."
        )

    # Can't start with a special character (period, hyphen, underscore)
    if file_id and file_id[0] in ['.', '-', '_']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File ID cannot start with a special character (period, hyphen, or underscore)."
        )

    return file_id


def validate_search_query(query: str, max_length: int = 500) -> str:
    """
    Validate search query.

    Args:
        query: Search query text
        max_length: Maximum query length

    Returns:
        Validated query

    Raises:
        HTTPException: If query is invalid
    """
    if not query or not query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty"
        )

    if len(query) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Search query exceeds maximum length ({max_length} characters)"
        )

    return query.strip()


def validate_user_id(user_id: str) -> str:
    """
    Validate user ID format.

    Args:
        user_id: User ID to validate

    Returns:
        Validated user ID

    Raises:
        HTTPException: If user ID is invalid
    """
    if not user_id or not user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is required"
        )

    # User ID should be alphanumeric with hyphens and underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format"
        )

    return user_id


def sanitize_path(path: str) -> str:
    """
    Sanitize file path to prevent path traversal attacks.

    Args:
        path: File path to sanitize

    Returns:
        Sanitized path
    """
    # Remove path traversal attempts
    path = path.replace('..', '')
    path = path.replace('//', '/')
    # Remove leading/trailing slashes
    path = path.strip('/')
    return path

