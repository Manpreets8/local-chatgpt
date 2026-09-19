import datetime

from pydantic import BaseModel, ConfigDict


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    generated_image_id: int | None = None
    created_at: datetime.datetime


class ConversationSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ConversationDetail(ConversationSummary):
    messages: list[MessageOut]
