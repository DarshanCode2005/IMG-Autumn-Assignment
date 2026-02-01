import os
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, Text
from typing import List, Optional
from datetime import datetime
from app.models.models import Photo
from app.schemas.photo import PhotoCreate, PhotoFilterParams
from pathlib import Path


def create_photo(
    db: Session,
    original_path: str,
    uploader_id: int,
    event_id: Optional[int] = None,
    processing_status: str = "pending"
) -> Photo:
    """Create a new photo record."""
    db_photo = Photo(
        original_path=original_path,
        uploader_id=uploader_id,
        event_id=event_id,
        processing_status=processing_status
    )
    db.add(db_photo)
    db.commit()
    db.refresh(db_photo)
    return db_photo


def get_photo(db: Session, photo_id: int) -> Optional[Photo]:
    """Get photo by ID."""
    return db.query(Photo).filter(Photo.id == photo_id).first()


def get_photos_by_event(db: Session, event_id: int, skip: int = 0, limit: int = 100) -> List[Photo]:
    """Get all photos for an event."""
    return db.query(Photo).filter(Photo.event_id == event_id).offset(skip).limit(limit).all()


def update_photo_processing(
    db: Session,
    photo_id: int,
    thumbnail_path: Optional[str] = None,
    watermarked_path: Optional[str] = None,
    exif_data: Optional[dict] = None,
    ai_tags: Optional[List[str]] = None,
    processing_status: str = "completed"
) -> Optional[Photo]:
    """Update photo processing results."""
    db_photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not db_photo:
        return None
    
    if thumbnail_path:
        db_photo.thumbnail_path = thumbnail_path
    if watermarked_path:
        db_photo.watermarked_path = watermarked_path
    if exif_data:
        db_photo.exif_data = exif_data
    if ai_tags:
        db_photo.ai_tags = ai_tags
    db_photo.processing_status = processing_status
    
    db.commit()
    db.refresh(db_photo)
    return db_photo
    db.commit()
    db.refresh(db_photo)
    return db_photo


def update_photo_tags(db: Session, photo_id: int, tags: List[str]) -> Optional[Photo]:
    """Update photo manual tags."""
    db_photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not db_photo:
        return None
    
    db_photo.manual_tags = tags
    db.commit()
    db.refresh(db_photo)
    return db_photo
def save_uploaded_file(file_content: bytes, filename: str, upload_dir: Path) -> str:
    """Save uploaded file to disk and return path with forward slashes."""
    upload_dir.mkdir(parents=True, exist_ok=True)
    filepath = upload_dir / filename
    with open(filepath, "wb") as f:
        f.write(file_content)
    return str(filepath).replace("\\", "/")


def search_photos(
    db: Session,
    filters: PhotoFilterParams,
    user_id: Optional[int] = None
) -> List[Photo]:
    """Advanced photo search with filtering."""
    query = db.query(Photo)
    
    # Filter by event
    if filters.event_id:
        query = query.filter(Photo.event_id == filters.event_id)
    
    # Filter by photographer (uploader)
    if filters.photographer_id:
        query = query.filter(Photo.uploader_id == filters.photographer_id)
    
    # Filter by date range
    if filters.date_from:
        query = query.filter(Photo.created_at >= filters.date_from)
    if filters.date_to:
        query = query.filter(Photo.created_at <= filters.date_to)
    
    # Filter by tags (using PostgreSQL JSONB array contains)
    if filters.tags:
        tag_conditions = []
        for tag in filters.tags:
            # Search in ai_tags JSONB array - check if any array element contains the tag
            # Using JSONB @> operator to check if array contains a value
            # For case-insensitive, we'll use a different approach
            tag_lower = tag.lower()
            # Check if ai_tags (as text) contains the tag (case-insensitive) OR manual_tags contains the tag
            tag_conditions.append(
                or_(
                    func.cast(Photo.ai_tags, Text).ilike(f"%{tag_lower}%"),
                    func.cast(Photo.manual_tags, Text).ilike(f"%{tag_lower}%")
                )
            )
        if tag_conditions:
            # Use OR for multiple tags (photo matches if it has any of the tags)
            query = query.filter(or_(*tag_conditions))
    
    # Only show completed photos (Commented out for debug)
    # query = query.filter(Photo.processing_status == "completed")
    
    # Order by creation date (newest first)
    query = query.order_by(Photo.created_at.desc())
    
    # Apply pagination
    photos = query.offset(filters.skip).limit(filters.limit).all()
    
    # Add engagement data
    from app.models.models import Like, Engagement
    for photo in photos:
        # Get engagement record
        engagement = db.query(Engagement).filter(Engagement.photo_id == photo.id).first()
        photo.likes_count = engagement.likes_count if engagement else 0
        
        # Check if user liked this photo (if user_id is provided)
        if user_id:
            like = db.query(Like).filter(
                Like.photo_id == photo.id,
                Like.user_id == user_id
            ).first()
            photo.is_liked = like is not None
        else:
            photo.is_liked = False
    
    return photos

