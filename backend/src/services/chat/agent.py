"""
Anthropic Claude chat service with citation extraction.
"""

import logging
import re
import time
from typing import AsyncGenerator, Optional

import anthropic

from src.config import get_settings
from src.models.conversation import Citation, StreamChunk

logger = logging.getLogger(__name__)


class ChatAgent:
    """
    Chat agent using Anthropic Claude API with citation support.

    Handles both synchronous and streaming responses.
    """

    def __init__(self) -> None:
        """Initialize chat agent with Anthropic client."""
        self.settings = get_settings()
        self.client = anthropic.AsyncAnthropic(api_key=self.settings.anthropic_api_key)

    async def generate_response(
        self,
        messages: list[dict[str, str]],
        selected_text: Optional[str] = None,
    ) -> tuple[str, list[Citation], int, int]:
        """
        Generate a chat response with citations.

        Args:
            messages: Conversation messages for context.
            selected_text: Original selected text for citation extraction.

        Returns:
            Tuple of (response_text, citations, tokens_used, latency_ms).
        """
        start_time = time.time()

        try:
            # Extract system message and convert to Claude format
            system_message = ""
            claude_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

            response = await self.client.messages.create(
                model=self.settings.anthropic_model,
                max_tokens=self.settings.anthropic_max_tokens,
                system=system_message,
                messages=claude_messages,
            )

            latency_ms = int((time.time() - start_time) * 1000)
            content = response.content[0].text if response.content else ""
            tokens_used = (response.usage.input_tokens + response.usage.output_tokens) if response.usage else 0

            # Extract citations from response
            citations = self._extract_citations(content, selected_text)

            return content, citations, tokens_used, latency_ms

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def generate_stream(
        self,
        messages: list[dict[str, str]],
        selected_text: Optional[str] = None,
    ) -> AsyncGenerator[StreamChunk, None]:
        """
        Generate a streaming chat response.

        Args:
            messages: Conversation messages for context.
            selected_text: Original selected text for citation extraction.

        Yields:
            StreamChunk objects for SSE transmission.
        """
        full_content = ""

        try:
            # Extract system message and convert to Claude format
            system_message = ""
            claude_messages = []

            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    claude_messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })

            async with self.client.messages.stream(
                model=self.settings.anthropic_model,
                max_tokens=self.settings.anthropic_max_tokens,
                system=system_message,
                messages=claude_messages,
            ) as stream:
                async for text in stream.text_stream:
                    full_content += text
                    yield StreamChunk(type="content", content=text)

            # Extract and yield citations after full response
            citations = self._extract_citations(full_content, selected_text)
            for citation in citations:
                yield StreamChunk(type="citation", citation=citation)

            yield StreamChunk(type="done")

        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            yield StreamChunk(type="error", error=str(e))

    def _extract_citations(
        self,
        response: str,
        selected_text: Optional[str],
    ) -> list[Citation]:
        """
        Extract citations from the response text.

        Identifies quoted text and matches to source material.

        Args:
            response: Generated response text.
            selected_text: Original selected text for matching.

        Returns:
            List of Citation objects.
        """
        citations: list[Citation] = []

        if not selected_text:
            return citations

        # Find quoted text in response (text within quotes)
        quote_patterns = [
            r'"([^"]{10,})"',  # Double quotes
            r"'([^']{10,})'",  # Single quotes
            r"`([^`]{10,})`",  # Backticks
        ]

        quoted_texts = set()
        for pattern in quote_patterns:
            matches = re.findall(pattern, response)
            quoted_texts.update(matches)

        # Match quotes against selected text
        selected_lower = selected_text.lower()
        for quote in quoted_texts:
            quote_lower = quote.lower()
            if quote_lower in selected_lower:
                # Calculate relevance based on match quality
                relevance = min(len(quote) / 100, 1.0)  # Longer quotes = higher relevance

                citations.append(
                    Citation(
                        text=quote[:200],  # Truncate long quotes
                        source_url="",  # Will be filled by caller
                        section_title=None,
                        relevance=round(relevance, 2),
                    )
                )

        # Also check for paraphrased content (fuzzy matching)
        sentences = selected_text.split(".")
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:
                continue

            # Check if key phrases appear in response
            words = sentence.lower().split()
            if len(words) < 5:
                continue

            # Check for 3+ consecutive words matching
            for i in range(len(words) - 2):
                phrase = " ".join(words[i : i + 3])
                if phrase in response.lower() and phrase not in [
                    c.text.lower() for c in citations
                ]:
                    citations.append(
                        Citation(
                            text=sentence[:200],
                            source_url="",
                            section_title=None,
                            relevance=0.7,
                        )
                    )
                    break

        # Deduplicate and limit citations
        seen = set()
        unique_citations = []
        for c in citations:
            key = c.text[:50].lower()
            if key not in seen:
                seen.add(key)
                unique_citations.append(c)

        return unique_citations[:5]  # Limit to top 5 citations
