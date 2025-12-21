from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.models import User
from app.crud.engagement import get_user_liked_photos, get_user_tagged_photos
from app.schemas.photo import PhotoWithEngagement

router = APIRouter(prefix="/me", tags=["user"])


@router.get("/library", response_model=List[PhotoWithEngagement])
def get_user_library(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get user's personal library:
    - Photos the user has liked
    - Photos where the user is tagged
    """
    # Get liked photos
    liked_photos = get_user_liked_photos(db, current_user.id, skip, limit)
    
    # Get tagged photos
    tagged_photos = get_user_tagged_photos(db, current_user.id, skip, limit)
    
    # Combine and deduplicate by photo ID
    photo_dict = {}
    for photo in liked_photos:
        photo_dict[photo.id] = photo
        photo.is_liked = True
    
    for photo in tagged_photos:
        if photo.id not in photo_dict:
            photo_dict[photo.id] = photo
        photo_dict[photo.id].is_tagged = True
    
    # Convert to list and add engagement data
    from app.models.models import Engagement, TaggedIn, Like
    result = []
    for photo in photo_dict.values():
        photo_dict_data = {
            "id": photo.id,
            "original_path": photo.original_path,
            "thumbnail_path": photo.thumbnail_path,
            "exif_data": photo.exif_data,
            "ai_tags": photo.ai_tags,
            "uploader_id": photo.uploader_id,
            "event_id": photo.event_id,
            "processing_status": photo.processing_status,
            "created_at": photo.created_at,
            "likes_count": 0,
            "is_liked": getattr(photo, "is_liked", False),
            "comments_count": 0,
            "tagged_users": []
        }
        
        # Get engagement data
        engagement = db.query(Engagement).filter(Engagement.photo_id == photo.id).first()
        if engagement:
            photo_dict_data["likes_count"] = engagement.likes_count
            from app.models.models import Comment
            comments_count = db.query(Comment).filter(Comment.engagement_id == engagement.id).count()
            photo_dict_data["comments_count"] = comments_count
        
        # Get tagged users
        tagged = db.query(TaggedIn).filter(TaggedIn.photo_id == photo.id).all()
        photo_dict_data["tagged_users"] = [t.user_id for t in tagged]
        
        result.append(PhotoWithEngagement(**photo_dict_data))
    
    return result

