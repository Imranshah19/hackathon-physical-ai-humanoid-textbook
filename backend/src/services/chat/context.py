"""
Context window management for chat conversations.

Manages selected text, RAG retrieval, and message history within token limits.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.conversation import Conversation, Message
from src.services.chat.retrieval import RetrievalService


class ContextService:
    """
    Service for managing chat context windows.

    Handles selected text context and message history with token budgets.
    """

    # Token budget allocation
    MAX_CONTEXT_TOKENS = 4096
    RAG_CONTEXT_BUDGET = 2000  # Max tokens for RAG retrieved context
    SELECTED_TEXT_BUDGET = 1000  # Max tokens for selected text
    HISTORY_BUDGET = 1000  # Max tokens for message history
    RESPONSE_BUDGET = 500  # Reserved for response

    # Message history limits
    MAX_HISTORY_TURNS = 20  # Maximum conversation turns to include

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize context service.

        Args:
            db: Async database session.
        """
        self.db = db
        self.retrieval = RetrievalService(top_k=5, score_threshold=0.7)

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Uses simple heuristic: ~4 chars per token for English.

        Args:
            text: Text to estimate.

        Returns:
            Estimated token count.
        """
        return len(text) // 4

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to approximate token limit.

        Args:
            text: Text to truncate.
            max_tokens: Maximum tokens allowed.

        Returns:
            Truncated text.
        """
        max_chars = max_tokens * 4
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + "..."

    async def get_conversation_history(
        self,
        conversation_id: UUID,
        max_turns: Optional[int] = None,
    ) -> list[Message]:
        """
        Get conversation message history.

        Args:
            conversation_id: Conversation to fetch.
            max_turns: Maximum number of turns (default: MAX_HISTORY_TURNS).

        Returns:
            List of messages in chronological order.
        """
        max_turns = max_turns or self.MAX_HISTORY_TURNS

        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(max_turns * 2)  # user + assistant messages per turn
        )
        messages = list(result.scalars().all())
        return list(reversed(messages))  # Return chronological order

    async def build_context_messages(
        self,
        selected_text: Optional[str],
        history: list[Message],
        user_message: str,
        page_url: Optional[str] = None,
    ) -> list[dict[str, str]]:
        """
        Build context messages for the chat model with RAG retrieval.

        Args:
            selected_text: User-selected documentation text.
            history: Previous conversation messages.
            user_message: Current user message.
            page_url: Current page URL for context filtering.

        Returns:
            List of message dicts for the chat API.
        """
        messages: list[dict[str, str]] = []

        # Retrieve relevant context using RAG
        rag_context = ""
        try:
            # Extract module from page URL if available
            module_filter = None
            if page_url:
                import re
                module_match = re.search(r"/(module-\d+)/", page_url)
                if module_match:
                    module_filter = module_match.group(1)

            # Retrieve relevant chunks
            chunks = await self.retrieval.retrieve(
                query=user_message,
                module_filter=module_filter,
            )
            rag_context = self.retrieval.format_context(
                chunks, max_tokens=self.RAG_CONTEXT_BUDGET
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"RAG retrieval failed: {e}")

        # System message with context
        system_content = self._build_system_prompt(selected_text, rag_context)
        messages.append({"role": "system", "content": system_content})

        # Add conversation history within token budget
        history_tokens = 0
        history_messages: list[dict[str, str]] = []

        for msg in history:
            msg_tokens = self._estimate_tokens(msg.content)
            if history_tokens + msg_tokens > self.HISTORY_BUDGET:
                break
            history_messages.append({
                "role": msg.role,
                "content": msg.content,
            })
            history_tokens += msg_tokens

        messages.extend(history_messages)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def _build_system_prompt(
        self,
        selected_text: Optional[str],
        rag_context: str = "",
    ) -> str:
        """
        Build system prompt with RAG and selected text context.

        Args:
            selected_text: User-selected documentation text.
            rag_context: Retrieved documentation context from RAG.

        Returns:
            System prompt string.
        """
        base_prompt = """You are an expert AI tutor for the "Physical AI & Humanoid Robotics" textbook. You help students understand robotics concepts including ROS 2, simulation, NVIDIA Isaac, and Vision-Language-Action models.

IMPORTANT RULES:
1. Only answer based on the provided context and documentation
2. If the answer is not in the context, say "I don't have enough information to answer that based on the textbook content"
3. Always cite your sources by referencing the section or module
4. Keep responses focused, educational, and concise
5. If asked about code, explain it clearly with examples from the documentation
6. For complex topics, break down explanations into steps
7. Encourage hands-on learning and refer students to relevant exercises"""

        prompt_parts = [base_prompt]

        # Add RAG retrieved context
        if rag_context:
            prompt_parts.append(f"""
RELEVANT TEXTBOOK CONTENT (retrieved from the documentation):
{rag_context}

Use this retrieved content to answer the user's question. Reference specific sections when relevant.""")

        # Add user selected text
        if selected_text:
            truncated = self._truncate_to_tokens(
                selected_text, self.SELECTED_TEXT_BUDGET
            )
            prompt_parts.append(f"""
USER SELECTED TEXT (highlighted by the user):
---
{truncated}
---

The user has highlighted this specific text. Address their question in relation to this selection.""")

        return "\n".join(prompt_parts)

    async def get_or_create_conversation(
        self,
        session_id: UUID,
        conversation_id: Optional[UUID],
        page_url: str,
        page_title: Optional[str],
        selected_text: Optional[str],
    ) -> Conversation:
        """
        Get existing conversation or create a new one.

        Args:
            session_id: User session ID.
            conversation_id: Existing conversation ID (if any).
            page_url: Documentation page URL.
            page_title: Page title.
            selected_text: User-selected text.

        Returns:
            Conversation instance.
        """
        if conversation_id:
            result = await self.db.execute(
                select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.session_id == session_id,
                )
            )
            conversation = result.scalar_one_or_none()
            if conversation:
                return conversation

        # Create new conversation
        conversation = Conversation(
            session_id=session_id,
            page_url=page_url,
            page_title=page_title,
            selected_text=selected_text[:5000] if selected_text else None,
        )
        self.db.add(conversation)
        await self.db.flush()
        return conversation

    async def add_message(
        self,
        conversation: Conversation,
        role: str,
        content: str,
        citations: Optional[list] = None,
        tokens_used: Optional[int] = None,
        latency_ms: Optional[int] = None,
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            conversation: Parent conversation.
            role: Message role (user/assistant).
            content: Message content.
            citations: Citation list for assistant messages.
            tokens_used: Token count.
            latency_ms: Response latency.

        Returns:
            Created Message.
        """
        message = Message(
            conversation_id=conversation.id,
            role=role,
            content=content,
            citations=citations or [],
            tokens_used=tokens_used,
            latency_ms=latency_ms,
        )
        self.db.add(message)
        await self.db.flush()
        return message
