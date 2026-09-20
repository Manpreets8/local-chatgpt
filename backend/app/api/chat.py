from anthropic import APIError
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import conversation_service
from app.services.llm_service import LLMNotConfiguredError, llm_service

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    is_new_conversation = request.conversation_id is None
    try:
        conversation = conversation_service.get_or_create_conversation(
            db, current_user.id, request.conversation_id
        )
    except conversation_service.ConversationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    # Stored history stays plain text even for image messages — resending
    # a full-size image on every later turn would be slow and expensive,
    # so an attached image only affects the current request to Claude.
    stored_text = request.message.strip() or "[Image attached]"
    conversation_service.add_message(db, conversation, "user", stored_text)
    if is_new_conversation:
        conversation.title = conversation_service.derive_title(stored_text)
    history = conversation_service.get_history_for_llm(conversation)

    if request.image_data:
        history[-1]["content"] = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": request.image_media_type,
                    "data": request.image_data,
                },
            },
            {"type": "text", "text": request.message.strip() or "What's in this image?"},
        ]

    try:
        reply = llm_service.chat(history)
    except LLMNotConfiguredError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except APIError as exc:
        db.rollback()
        cause = f" | cause: {exc.__cause__!r}" if exc.__cause__ else ""
        raise HTTPException(
            status_code=502, detail=f"AI service error: {exc!r}{cause}"
        ) from exc

    conversation_service.add_message(db, conversation, "assistant", reply)
    db.commit()

    return ChatResponse(reply=reply, conversation_id=conversation.id)
