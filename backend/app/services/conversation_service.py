from typing import Any

from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message


class ConversationNotFoundError(Exception):
    def __init__(self, conversation_id: int) -> None:
        super().__init__(f"Conversation {conversation_id} not found.")
        self.conversation_id = conversation_id


def get_or_create_conversation(db: Session, conversation_id: int | None) -> Conversation:
    """Existing conversations continue the same thread (short-term memory);
    no id means start a fresh one. Nothing here writes to any long-term
    memory store — a conversation's history only lives as long as its rows."""
    if conversation_id is not None:
        conversation = db.get(Conversation, conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)
        return conversation

    conversation = Conversation()
    db.add(conversation)
    db.flush()
    return conversation


def add_message(db: Session, conversation: Conversation, role: str, content: str) -> Message:
    message = Message(conversation_id=conversation.id, role=role, content=content)
    db.add(message)
    db.flush()
    return message


def get_history_for_llm(conversation: Conversation) -> list[dict[str, Any]]:
    return [{"role": m.role, "content": m.content} for m in conversation.messages]


def derive_title(first_message: str, max_length: int = 50) -> str:
    stripped = first_message.strip()
    if len(stripped) <= max_length:
        return stripped
    return stripped[:max_length].rstrip() + "…"
