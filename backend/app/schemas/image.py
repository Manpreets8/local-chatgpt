from pydantic import BaseModel, Field


class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    conversation_id: int | None = None


class ImageGenerateResponse(BaseModel):
    image_id: int
    image_data: str
    conversation_id: int
