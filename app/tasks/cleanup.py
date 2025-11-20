import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import select

from app.db.session import get_session_sync
from app.db.models import Image
from app.services.storage import delete_object
from app.core.config import settings


def cleanup_expired_images():
    """
    Deletes images older than configured retention time
    from Cloudflare R2 and marks database accordingly.
    """

    cutoff = datetime.datetime.utcnow() - datetime.timedelta(
        hours=settings.IMAGE_RETENTION_HOURS
    )

    with get_session_sync() as session:
        stmt = select(Image).where(Image.uploaded_at < cutoff)
        old_images = session.exec(stmt).all()

        for img in old_images:
            try:
                # delete file from R2
                delete_object(img.s3_key)
            except:
                pass

            # update DB
            session.delete(img)

        session.commit()


def start_scheduler():
    """
    Runs every 1 hour to delete old images.
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(cleanup_expired_images, "interval", hours=1)
    scheduler.start()


