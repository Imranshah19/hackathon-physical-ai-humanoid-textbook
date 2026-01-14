"""
Translation service for chapter content.

Translates text to Urdu using OpenAI's API.
"""

import logging
from typing import Optional

from openai import AsyncOpenAI

from src.config import get_settings

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for translating chapter content to Urdu."""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def translate_to_urdu(
        self,
        text: str,
        preserve_code: bool = True,
    ) -> str:
        """
        Translate text to Urdu.

        Args:
            text: Text to translate
            preserve_code: If True, keep code blocks untranslated

        Returns:
            Translated text in Urdu
        """
        if not text or not text.strip():
            return text

        system_prompt = """You are a professional translator specializing in technical and educational content.
Translate the following text from English to Urdu (اردو).

Guidelines:
- Maintain the technical accuracy of the content
- Keep proper nouns, brand names, and technical terms that don't have common Urdu equivalents in English
- Preserve any code snippets, URLs, or file paths exactly as they are
- Maintain the formatting structure (paragraphs, lists, etc.)
- Use formal Urdu appropriate for educational textbooks
- Ensure the translation reads naturally for Urdu speakers"""

        if preserve_code:
            system_prompt += """
- Do NOT translate text inside code blocks (```...```) or inline code (`...`)
- Keep variable names, function names, and programming syntax unchanged"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=0.3,  # Lower temperature for more consistent translations
                max_tokens=4096,
            )

            translated = response.choices[0].message.content
            logger.info(f"Translated {len(text)} chars to Urdu ({len(translated)} chars)")
            return translated

        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise TranslationError(f"Failed to translate text: {str(e)}")


class TranslationError(Exception):
    """Exception raised when translation fails."""

    pass


# Singleton instance
_translation_service: Optional[TranslationService] = None


def get_translation_service() -> TranslationService:
    """Get or create the translation service singleton."""
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service
