from pydantic import BaseModel, Field, model_validator

ALLOWED_IMAGE_MEDIA_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}
MAX_IMAGE_BASE64_CHARS = 6_000_000  # ~4.5MB decoded, generous for a chat attachment


class ChatRequest(BaseModel):
    message: str = Field("", max_length=4000)
    conversation_id: int | None = None
    image_data: str | None = Field(None, max_length=MAX_IMAGE_BASE64_CHARS)
    image_media_type: str | None = None

    @model_validator(mode="after")
    def validate_content(self) -> "ChatRequest":
        if not self.message.strip() and not self.image_data:
            raise ValueError("Message must include text or an image.")
        if self.image_data and self.image_media_type not in ALLOWED_IMAGE_MEDIA_TYPES:
            raise ValueError(
                f"Unsupported image type. Allowed: {', '.join(sorted(ALLOWED_IMAGE_MEDIA_TYPES))}"
            )
        return self


class ChatResponse(BaseModel):
    reply: str
    conversation_id: int
