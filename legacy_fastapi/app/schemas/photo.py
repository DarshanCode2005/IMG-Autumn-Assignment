from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


class PhotoBase(BaseModel):
    event_id: Optional[int] = None


class PhotoCreate(PhotoBase):
    pass


class Photo(PhotoBase):
    id: int
    original_path: str
    thumbnail_path: Optional[str] = None
    exif_data: Optional[Dict[str, Any]] = None
    ai_tags: Optional[List[str]] = None
    manual_tags: Optional[List[str]] = None
    uploader_id: int
    processing_status: str
    created_at: datetime
    likes_count: Optional[int] = 0
    is_liked: Optional[bool] = False

    model_config = ConfigDict(from_attributes=True)


class PhotoUpdate(BaseModel):
    manual_tags: List[str]


class PhotoUploadResponse(BaseModel):
    photo_id: int
    message: str
    processing_status: str


class PhotoFilterParams(BaseModel):
    event_id: Optional[int] = None
    photographer_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    tags: Optional[List[str]] = None
    skip: int = 0
    limit: int = 100


class PhotoWithEngagement(Photo):
    """Photo with engagement data."""
    comments_count: Optional[int] = 0
    tagged_users: Optional[List[int]] = None

    model_config = ConfigDict(from_attributes=True)
