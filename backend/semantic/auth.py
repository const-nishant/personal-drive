"""Authentication utilities for API key validation."""

import logging
from fastapi import Header, HTTPException, status
from typing import Annotated

from config import Config

logger = logging.getLogger(__name__)


async def verify_api_key(
    x_api_key: Annotated[str, Header(alias="X-API-Key")]
) -> str:
    """
    Verify API key from request header.

    Args:
        x_api_key: API key from X-API-Key header

    Returns:
        The verified API key

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if x_api_key != Config.API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key. Provide X-API-Key header."
        )
    return x_api_key


async def get_user_id(
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None
) -> str:
    """
    Get and validate user ID from request header.

    Args:
        x_user_id: User ID from X-User-Id header

    Returns:
        The user ID

    Raises:
        HTTPException: If user ID is missing
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User ID is required. Provide X-User-Id header."
        )
    return x_user_id

