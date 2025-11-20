import cv2
import numpy as np
import tempfile
import os
from uuid import uuid4
from sqlmodel import select
import datetime

from app.core.config import settings
from app.db.session import get_session_sync
from app.db.models import Image, Recommendation
from app.services.storage import delete_object
from app.services.rules_engine import generate_recommendations_for_features
from app.services.recommender import map_templates_to_products

import boto3
from botocore.client import Config


# Load OpenCV face detector
HAAR_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(HAAR_PATH)


def bgr_to_hex(bgr):
    r, g, b = int(bgr[2]), int(bgr[1]), int(bgr[0])
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def extract_skin_tone_from_face(img_bgr, face_box):
    x, y, w, h = face_box

    # Crop a clean central region from the face (reduces errors)
    x0 = x + int(w * 0.20)
    y0 = y + int(h * 0.20)
    x1 = x + int(w * 0.80)
    y1 = y + int(h * 0.80)

    roi = img_bgr[y0:y1, x0:x1]

    if roi.size == 0:
        return {"tone": "unknown", "hex": "#808080"}

    # Convert to LAB space for lightness measurement
    lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
    L = lab[:, :, 0]
    mean_light = np.mean(L)

    # Categorize into NON-OFFENSIVE buckets
    if mean_light >= 200:
        tone = "very_light"
    elif mean_light >= 150:
        tone = "light"
    elif mean_light >= 100:
        tone = "medium"
    else:
        tone = "dark"

    avg_color = roi.mean(axis=(0, 1))

    return {
        "tone": tone,
        "hex": bgr_to_hex(avg_color)
    }


def estimate_body_bbox(img_bgr):
    """
    A simple estimation to locate the user's body.
    Creates a wide box based on the image size.
    """
    h, w = img_bgr.shape[:2]

    x = int(w * 0.10)
    y = int(h * 0.05)
    bw = int(w * 0.80)
    bh = int(h * 0.90)

    return {"x": x, "y": y, "w": bw, "h": bh}


def process_downloaded_image(local_path: str):
    img = cv2.imread(local_path)

    if img is None:
        return {}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50)
    )

    features = {}

    # If a face was found → extract skin tone
    if len(faces) > 0:
        face = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[0]
        features["face_bbox"] = {
            "x": int(face[0]),
            "y": int(face[1]),
            "w": int(face[2]),
            "h": int(face[3])
        }
        features["skin_tone"] = extract_skin_tone_from_face(img, face)
    else:
        # Still work even if no face is detected
        features["skin_tone"] = {"tone": "unknown", "hex": "#808080"}

    # Estimate the body region
    features["body_bbox"] = estimate_body_bbox(img)

    # Useful for proportion-based styling rules
    h, w = img.shape[:2]
    features["image_ratio"] = round(h / w, 3)

    return features


def process_image_task(image_id: str, s3_key: str, occasion: str):
    """
    MAIN PIPELINE:
    - Downloads the uploaded image
    - Process it using OpenCV
    - Saves extracted features to DB
    - Generates outfit recommendations
    """

    # STEP 1 — Download image from Cloudflare R2
    s3 = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        config=Config(signature_version="s3v4")
    )

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")

    try:
        s3.download_file(settings.S3_BUCKET, s3_key, temp.name)
    except Exception:
        temp.close()
        os.unlink(temp.name)

        # Update DB → failed
        with get_session_sync() as session:
            img = session.get(Image, image_id)
            if img:
                img.status = "failed"
                session.add(img)
                session.commit()
        return

    temp.close()

    # STEP 2 — Extract features
    features = process_downloaded_image(temp.name)

    # STEP 3 — Save to database
    with get_session_sync() as session:
        img_record = session.get(Image, image_id)

        if img_record:
            img_record.status = "processed"
            img_record.processed_at = datetime.datetime.utcnow()

            # Optional: save summary for quick access
            img_record.skin_tone = features.get("skin_tone", {}).get("tone")
            img_record.body_shape = features.get("body_bbox", None)
            img_record.proportions = str(features.get("image_ratio"))

            session.add(img_record)
            session.commit()

    # STEP 4 — Generate outfit recommendations
    templates = generate_recommendations_for_features(features, occasion)

    # STEP 5 — Map templates to product picks
    ranked = map_templates_to_products(templates)

    # STEP 6 — Store recommendation record
    with get_session_sync() as session:
        rec = Recommendation(
            id=str(uuid4()),
            image_id=image_id,
            ranked_outfits=ranked,
            created_at=datetime.datetime.utcnow()
        )
        session.add(rec)
        session.commit()

    # Cleanup: delete temp file
    try:
        os.unlink(temp.name)
    except:
        pass

    # (Image will be deleted from R2 after 24 hours by cleanup job)

