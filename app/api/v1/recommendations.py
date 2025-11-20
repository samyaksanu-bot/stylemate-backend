from fastapi import APIRouter, HTTPException
from app.db.session import get_session_sync
from app.db.models import Recommendation
from sqlmodel import select

router = APIRouter()

@router.get("/{image_id}")
def get_recommendation(image_id: str):
    with get_session_sync() as session:
        stmt = select(Recommendation).where(Recommendation.image_id == image_id)
        rec = session.exec(stmt).one_or_none()

        if not rec:
            raise HTTPException(
                status_code=404,
                detail="Recommendation not found or still processing"
            )

        return {
            "image_id": image_id,
            "recommendation": rec.ranked_outfits
        }


   