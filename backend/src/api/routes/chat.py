"""
Chat API endpoints for the RAG documentation chatbot.
"""

import json
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.postgres import get_db_session
from src.models.conversation import (
    ChatRequest,
    ChatResponse,
    MessageSchema,
    StreamChunk,
)
from src.services.chat.agent import ChatAgent
from src.services.chat.context import ContextService
from src.services.session import SessionService

logger = logging.getLogger(__name__)
router = APIRouter()


async def get_session_id(
    x_session_token: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db_session),
) -> UUID:
    """
    Get or create session from header token.

    Args:
        x_session_token: Session token from header.
        db: Database session.

    Returns:
        Session UUID.

    Raises:
        HTTPException: If session creation fails.
    """
    session_service = SessionService(db)
    session, created = await session_service.get_or_create_session(x_session_token)

    if created:
        logger.info(f"Created new session: {session.id}")

    return session.id


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session_id: UUID = Depends(get_session_id),
    db: AsyncSession = Depends(get_db_session),
) -> ChatResponse:
    """
    Send a chat message and receive a response with citations.

    This endpoint processes the message synchronously and returns
    the complete response.

    Args:
        request: Chat request with message and context.
        session_id: User session ID.
        db: Database session.

    Returns:
        ChatResponse with message and conversation ID.
    """
    context_service = ContextService(db)
    chat_agent = ChatAgent()

    # Get or create conversation
    conversation = await context_service.get_or_create_conversation(
        session_id=session_id,
        conversation_id=request.conversation_id,
        page_url=request.page_url,
        page_title=request.page_title,
        selected_text=request.selected_text,
    )

    # Get conversation history for follow-ups
    history = []
    if request.conversation_id:
        history = await context_service.get_conversation_history(conversation.id)

    # Build context messages with RAG retrieval
    messages = await context_service.build_context_messages(
        selected_text=conversation.selected_text,
        history=history,
        user_message=request.message,
        page_url=request.page_url,
    )

    # Save user message
    await context_service.add_message(
        conversation=conversation,
        role="user",
        content=request.message,
    )

    # Generate response
    try:
        response_text, citations, tokens_used, latency_ms = await chat_agent.generate_response(
            messages=messages,
            selected_text=conversation.selected_text,
        )

        # Add source URL to citations
        for citation in citations:
            citation.source_url = request.page_url

        # Save assistant message
        assistant_message = await context_service.add_message(
            conversation=conversation,
            role="assistant",
            content=response_text,
            citations=[c.model_dump() for c in citations],
            tokens_used=tokens_used,
            latency_ms=latency_ms,
        )

        await db.commit()

        return ChatResponse(
            message=MessageSchema.model_validate(assistant_message),
            conversation_id=conversation.id,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to generate response")


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    session_id: UUID = Depends(get_session_id),
    db: AsyncSession = Depends(get_db_session),
) -> StreamingResponse:
    """
    Send a chat message and receive a streaming response (SSE).

    This endpoint streams the response in real-time using
    Server-Sent Events.

    Args:
        request: Chat request with message and context.
        session_id: User session ID.
        db: Database session.

    Returns:
        StreamingResponse with SSE events.
    """
    context_service = ContextService(db)
    chat_agent = ChatAgent()

    # Get or create conversation
    conversation = await context_service.get_or_create_conversation(
        session_id=session_id,
        conversation_id=request.conversation_id,
        page_url=request.page_url,
        page_title=request.page_title,
        selected_text=request.selected_text,
    )

    # Get conversation history
    history = []
    if request.conversation_id:
        history = await context_service.get_conversation_history(conversation.id)

    # Build context messages with RAG retrieval
    messages = await context_service.build_context_messages(
        selected_text=conversation.selected_text,
        history=history,
        user_message=request.message,
        page_url=request.page_url,
    )

    # Save user message
    await context_service.add_message(
        conversation=conversation,
        role="user",
        content=request.message,
    )
    await db.commit()

    async def generate_stream():
        """Generate SSE stream."""
        full_content = ""
        all_citations = []

        try:
            async for chunk in chat_agent.generate_stream(
                messages=messages,
                selected_text=conversation.selected_text,
            ):
                if chunk.type == "content":
                    full_content += chunk.content or ""

                if chunk.type == "citation" and chunk.citation:
                    chunk.citation.source_url = request.page_url
                    all_citations.append(chunk.citation)

                # Format as SSE
                data = chunk.model_dump_json()
                yield f"data: {data}\n\n"

            # Save assistant message after stream completes
            async with get_db_session() as save_db:
                save_context = ContextService(save_db)
                await save_context.add_message(
                    conversation=conversation,
                    role="assistant",
                    content=full_content,
                    citations=[c.model_dump() for c in all_citations],
                )
                await save_db.commit()

        except Exception as e:
            logger.error(f"Stream error: {e}")
            error_chunk = StreamChunk(type="error", error=str(e))
            yield f"data: {error_chunk.model_dump_json()}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Conversation-ID": str(conversation.id),
        },
    )


@router.post("/messages/{message_id}/feedback")
async def submit_feedback(
    message_id: UUID,
    feedback: str,
    session_id: UUID = Depends(get_session_id),
    db: AsyncSession = Depends(get_db_session),
) -> dict:
    """
    Submit feedback for a message.

    Args:
        message_id: Message to rate.
        feedback: "up" or "down".
        session_id: User session.
        db: Database session.

    Returns:
        Success status.
    """
    from sqlalchemy import select, update
    from src.models.conversation import Message, Conversation

    if feedback not in ("up", "down"):
        raise HTTPException(status_code=400, detail="Feedback must be 'up' or 'down'")

    # Verify message belongs to user's session
    result = await db.execute(
        select(Message)
        .join(Conversation)
        .where(
            Message.id == message_id,
            Conversation.session_id == session_id,
        )
    )
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message.feedback = feedback
    await db.commit()

    return {"success": True, "message_id": str(message_id), "feedback": feedback}
