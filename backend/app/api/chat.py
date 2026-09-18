from anthropic import APIError
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services import conversation_service
from app.services.llm_service import LLMNotConfiguredError, llm_service

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    is_new_conversation = request.conversation_id is None
    try:
        conversation = conversation_service.get_or_create_conversation(
            db, request.conversation_id
        )
    except conversation_service.ConversationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    conversation_service.add_message(db, conversation, "user", request.message)
    if is_new_conversation:
        conversation.title = conversation_service.derive_title(request.message)
    history = conversation_service.get_history_for_llm(conversation)

    try:
        reply = llm_service.chat(history)
    except LLMNotConfiguredError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except APIError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=f"AI service error: {exc}") from exc

    conversation_service.add_message(db, conversation, "assistant", reply)
    db.commit()

    return ChatResponse(reply=reply, conversation_id=conversation.id)
