from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    IMAGE_RETENTION_HOURS: int
    MAX_IMAGE_SIZE_BYTES: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
