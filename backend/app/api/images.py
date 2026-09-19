import base64
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.generated_image import GeneratedImage
from app.models.user import User
from app.schemas.image import ImageGenerateRequest, ImageGenerateResponse
from app.services import conversation_service
from app.services.image_service import ImageServiceError, NoImageReturnedError, image_service

router = APIRouter(prefix="/images", tags=["images"])

GENERATED_DIR = Path(__file__).resolve().parents[3] / "data" / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/generate", response_model=ImageGenerateResponse, status_code=201)
def generate_image(
    request: ImageGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ImageGenerateResponse:
    try:
        conversation = conversation_service.get_or_create_conversation(
            db, current_user.id, request.conversation_id
        )
    except conversation_service.ConversationNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    is_new_conversation = request.conversation_id is None
    conversation_service.add_message(db, conversation, "user", request.prompt)
    if is_new_conversation:
        conversation.title = conversation_service.derive_title(request.prompt)

    try:
        result_bytes, content_type = image_service.generate_image(request.prompt)
    except NoImageReturnedError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ImageServiceError as exc:
        db.rollback()
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    image_record = GeneratedImage(
        user_id=current_user.id, prompt=request.prompt, content_type=content_type
    )
    db.add(image_record)
    db.flush()

    (GENERATED_DIR / str(image_record.id)).write_bytes(result_bytes)

    conversation_service.add_message(
        db,
        conversation,
        "assistant",
        "Here's your generated image.",
        generated_image_id=image_record.id,
    )
    db.commit()

    return ImageGenerateResponse(
        image_id=image_record.id,
        image_data=base64.b64encode(result_bytes).decode(),
        conversation_id=conversation.id,
    )


@router.get("/{image_id}")
def get_generated_image(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    image_record = db.get(GeneratedImage, image_id)
    if image_record is None or image_record.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Image not found")

    file_path = GENERATED_DIR / str(image_id)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image file not found")

    return Response(content=file_path.read_bytes(), media_type=image_record.content_type)
