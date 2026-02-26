"""
Translation API endpoints for chapter content.
"""

import logging

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.services.translation import (
    TranslationService,
    TranslationError,
    get_translation_service,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/translate", tags=["translate"])


class TranslateRequest(BaseModel):
    """Request to translate text."""

    text: str = Field(..., min_length=1, max_length=10000, description="Text to translate")
    preserve_code: bool = Field(
        default=True, description="Keep code blocks untranslated"
    )


class TranslateResponse(BaseModel):
    """Response with translated text."""

    original: str
    translated: str
    target_language: str = "ur"  # Urdu ISO code
    target_language_name: str = "اردو"


@router.post("/urdu", response_model=TranslateResponse)
async def translate_to_urdu(request: TranslateRequest) -> TranslateResponse:
    """
    Translate text to Urdu.

    Translates chapter content while preserving code blocks and technical terms.
    """
    service = get_translation_service()

    try:
        translated = await service.translate_to_urdu(
            text=request.text,
            preserve_code=request.preserve_code,
        )

        return TranslateResponse(
            original=request.text,
            translated=translated,
        )

    except TranslationError as e:
        logger.error(f"Translation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Unexpected translation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Translation service unavailable",
        )
