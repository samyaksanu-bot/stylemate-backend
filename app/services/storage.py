import boto3
from botocore.client import Config
from app.core.config import settings

# Initialize S3 client for Cloudflare R2
s3 = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT_URL,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    config=Config(signature_version="s3v4")
)

def upload_bytes(key: str, data: bytes, content_type: str = "image/jpeg"):
    """
    Upload raw bytes to Cloudflare R2 storage.
    """
    s3.put_object(
        Bucket=settings.S3_BUCKET,
        Key=key,
        Body=data,
        ContentType=content_type,
        ACL="private"
    )
    return key

def delete_object(key: str):
    """
    Permanently delete file from Cloudflare R2.
    """
    s3.delete_object(Bucket=settings.S3_BUCKET, Key=key)

def generate_presigned_url(key: str, expires_in=3600):
    """
    Generate a temporary URL so frontend can view images securely.
    """
    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": key},
        ExpiresIn=expires_in
    )
