from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from uuid import uuid4
import datetime
from app.core.config import settings
from app.services import storage
from app.services.processing import process_image_task
from app.db.session import get_session_sync, create_db_and_tables
from app.db.models import Image
from sqlmodel import select

router = APIRouter()

@router.post("/")
async def upload_image(
    background_tasks: BackgroundTasks,
    image: UploadFile = File(...),
    occasion: str = Form(...),
    user_id: str | None = Form(None)
):
    # Check file type
    if image.content_type.split("/")[0] != "image":
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Read content
    contents = await image.read()

    # Check size
    if len(contents) > settings.MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File too large")

    # Generate a unique ID
    image_id = str(uuid4())
    s3_key = f"uploads/{image_id}_{image.filename}"

    # Upload to Cloudflare R2
    storage.upload_bytes(s3_key, contents, content_type=image.content_type)

    # Save DB record
    create_db_and_tables()
    with get_session_sync() as session:
        img = Image(
            id=image_id,
            user_id=user_id,
            s3_key=s3_key,
            uploaded_at=datetime.datetime.utcnow(),
            status="pending"
        )
        session.add(img)
        session.commit()

    # Start background processing
    background_tasks.add_task(process_image_task, image_id, s3_key, occasion)

    return {
        "image_id": image_id,
        "status": "processing"
    }

