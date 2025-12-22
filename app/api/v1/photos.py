from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks, Query, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
from datetime import datetime
import uuid
import os
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_optional_user
from app.models.models import User
from app.crud.photo import create_photo, save_uploaded_file, search_photos, get_photo, update_photo_tags
from app.crud.engagement import (
    toggle_like, create_comment, get_comments_by_photo,
    get_user_liked_photos, get_user_tagged_photos
)
from app.schemas.photo import PhotoUploadResponse, Photo, PhotoFilterParams, PhotoWithEngagement, PhotoUpdate
from app.schemas.engagement import LikeResponse, CommentCreate, CommentResponse
from app.worker.tasks import process_photo_task

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("/upload", response_model=List[PhotoUploadResponse], status_code=status.HTTP_201_CREATED)
async def upload_photos(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    event_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Upload multiple photos. Each photo will be processed asynchronously via Celery.
    """
    print(f"DEBUG: upload_photos called with {len(files)} files and event_id: {event_id}")

    uploader_id = None
    if current_user:
        uploader_id = current_user.id
    else:
        # Fallback for development (skipping auth)
        first_user = db.query(User).first()
        if first_user:
            uploader_id = first_user.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No uploader found. Please create a user first."
            )

    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files provided"
        )
    
    # Validate file types
    allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
    uploaded_photos = []
    
    media_dir = Path("media/originals")
    media_dir.mkdir(parents=True, exist_ok=True)
    
    for file in files:
        # Check file extension
        filename = file.filename or f"upload_{uuid.uuid4()}.jpg"
        file_ext = Path(filename).suffix.lower()
        if not file_ext:
            file_ext = ".jpg"
            
        print(f"DEBUG: Processing file: {filename} with extension: {file_ext}")
            
        if file_ext not in allowed_extensions:
            print(f"DEBUG: Skipping file with invalid extension: {file_ext}")
            continue
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Read file content
        file_content = await file.read()
        
        # Save file
        original_path = save_uploaded_file(file_content, unique_filename, media_dir)
        print(f"DEBUG: Saved file to: {original_path}")
        
        # Create photo record
        db_photo = create_photo(
            db=db,
            original_path=original_path,
            uploader_id=uploader_id,
            event_id=event_id,
            processing_status="pending"
        )
        
        # Trigger Celery task directly
        print(f"DEBUG: Enqueuing Celery task for photo_id: {db_photo.id}")
        process_photo_task.delay(db_photo.id, str(original_path))
        
        uploaded_photos.append({
            "photo_id": db_photo.id,
            "message": f"Photo {filename} uploaded successfully",
            "processing_status": "pending"
        })
    
    if not uploaded_photos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid image files provided"
        )
    
    return uploaded_photos


@router.get("/", response_model=List[PhotoWithEngagement])
def get_photos(
    event_id: Optional[int] = Query(None, description="Filter by event ID"),
    photographer_id: Optional[int] = Query(None, description="Filter by photographer (uploader) ID"),
    date_from: Optional[datetime] = Query(None, description="Filter photos from this date"),
    date_to: Optional[datetime] = Query(None, description="Filter photos until this date"),
    tags: Optional[str] = Query(None, description="Comma-separated list of tags to search"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Advanced photo search with filtering by:
    - Event ID
    - Photographer ID
    - Date range
    - Tags (searches in AI-generated tags)
    """
    # Parse tags if provided
    tag_list = None
    if tags:
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    filters = PhotoFilterParams(
        event_id=event_id,
        photographer_id=photographer_id,
        date_from=date_from,
        date_to=date_to,
        tags=tag_list,
        skip=skip,
        limit=limit
    )
    
    user_id = current_user.id if current_user else None
    photos = search_photos(db, filters, user_id)
    
    # Add engagement data
    from app.models.models import Engagement, TaggedIn
    result = []
    for photo in photos:
        photo_dict = {
            "id": photo.id,
            "original_path": photo.original_path,
            "thumbnail_path": photo.thumbnail_path,
            "exif_data": photo.exif_data,
            "ai_tags": photo.ai_tags,
            "uploader_id": photo.uploader_id,
            "event_id": photo.event_id,
            "processing_status": photo.processing_status,
            "created_at": photo.created_at,
            "likes_count": getattr(photo, "likes_count", 0),
            "is_liked": getattr(photo, "is_liked", False),
            "comments_count": 0,
            "tagged_users": []
        }
        
        # Get comments count
        engagement = db.query(Engagement).filter(Engagement.photo_id == photo.id).first()
        if engagement:
            from app.models.models import Comment
            comments_count = db.query(Comment).filter(Comment.engagement_id == engagement.id).count()
            photo_dict["comments_count"] = comments_count
        
        # Get tagged users
        tagged = db.query(TaggedIn).filter(TaggedIn.photo_id == photo.id).all()
        photo_dict["tagged_users"] = [t.user_id for t in tagged]
        
        result.append(PhotoWithEngagement(**photo_dict))
    
    return result


@router.put("/{photo_id}", response_model=Photo)
def update_photo(
    photo_id: int,
    photo_update: PhotoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update photo details (e.g. manual tags)."""
    # Verify photo exists
    photo = get_photo(db, photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )
    
    # Check permissions (only uploader, admin, or coordinator)
    if current_user.id != photo.uploader_id and current_user.role not in ["Admin", "Coordinator"]:
         raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this photo"
        )
        
    updated_photo = update_photo_tags(db, photo_id, photo_update.manual_tags)
    return updated_photo


@router.post("/{photo_id}/like", response_model=LikeResponse)
def like_photo(
    photo_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Toggle like on a photo. Supports skipping auth for dev."""
    # Verify photo exists
    photo = get_photo(db, photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )
    
    user_id = None
    if current_user:
        user_id = current_user.id
    else:
        # Fallback for development
        first_user = db.query(User).first()
        if first_user:
            user_id = first_user.id
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No user found to like the photo."
            )
    
    result = toggle_like(db, photo_id, user_id)
    return result


@router.get("/{photo_id}/download")
def download_photo(
    photo_id: int,
    db: Session = Depends(get_db)
):
    """Download the original photo."""
    from fastapi.responses import FileResponse
    photo = get_photo(db, photo_id)
    if not photo or not os.path.exists(photo.original_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo file not found"
        )
    
    return FileResponse(
        path=photo.original_path,
        filename=os.path.basename(photo.original_path),
        media_type="image/jpeg"
    )


@router.post("/{photo_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_photo_comment(
    photo_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """Create a comment on a photo. Supports threaded replies via parent_id."""
    # Verify photo exists
    photo = get_photo(db, photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )
    
    user_id = None
    user_email = None
    if current_user:
        user_id = current_user.id
        user_email = current_user.email
    else:
        # Fallback for development
        first_user = db.query(User).first()
        if first_user:
            user_id = first_user.id
            user_email = first_user.email
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No uploader found. Please create a user first."
            )

    # If parent_id is provided, verify parent comment exists
    if comment.parent_id:
        from app.models.models import Comment, Engagement
        engagement = db.query(Engagement).filter(Engagement.photo_id == photo_id).first()
        if engagement:
            parent = db.query(Comment).filter(
                Comment.id == comment.parent_id,
                Comment.engagement_id == engagement.id
            ).first()
            if not parent:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent comment not found"
                )
    
    db_comment = create_comment(db, photo_id, user_id, comment)
    
    # Return with author email
    return CommentResponse(
        id=db_comment.id,
        engagement_id=db_comment.engagement_id,
        author_id=db_comment.author_id,
        content=db_comment.content,
        parent_id=db_comment.parent_id,
        created_at=db_comment.created_at,
        author_email=user_email,
        replies=None
    )


@router.get("/{photo_id}/comments", response_model=List[CommentResponse])
def get_photo_comments(
    photo_id: int,
    db: Session = Depends(get_db)
):
    """Get all comments for a photo, organized in threads."""
    # Verify photo exists
    photo = get_photo(db, photo_id)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Photo not found"
        )
    
    comments = get_comments_by_photo(db, photo_id)
    
    # Build response with author emails
    from app.models.models import User
    result = []
    for comment in comments:
        author = db.query(User).filter(User.id == comment.author_id).first()
        result.append(CommentResponse(
            id=comment.id,
            engagement_id=comment.engagement_id,
            author_id=comment.author_id,
            content=comment.content,
            parent_id=comment.parent_id,
            created_at=comment.created_at,
            author_email=author.email if author else None,
            replies=None
        ))
    
    return result
