from sqlmodel import SQLModel, Field, JSON
import datetime
from typing import Optional, List


class User(SQLModel, table=True):
    id: str = Field(primary_key=True)
    email: str
    password_hash: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class Image(SQLModel, table=True):
    id: str = Field(primary_key=True)
    user_id: Optional[str] = Field(default=None)
    s3_key: str
    uploaded_at: datetime.datetime
    processed_at: Optional[datetime.datetime] = None
    status: str  # pending / processed / failed
    skin_tone: Optional[str] = None
    body_shape: Optional[str] = None
    proportions: Optional[str] = None


class Recommendation(SQLModel, table=True):
    id: str = Field(primary_key=True)
    image_id: str
    ranked_outfits: JSON  # this will store the 5 recommendations as JSON
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class Product(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    image_url: str
    price: float
    category: str
    color: str
    tags: str
    link: str
