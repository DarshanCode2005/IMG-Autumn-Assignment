from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import Optional, List
from datetime import datetime
from app.models.models import Like, Comment, Engagement, TaggedIn, Photo
from app.schemas.engagement import CommentCreate


def toggle_like(db: Session, photo_id: int, user_id: int) -> dict:
    """Toggle like on a photo. Returns like status and updated count."""
    # Check if like exists
    existing_like = db.query(Like).filter(
        Like.photo_id == photo_id,
        Like.user_id == user_id
    ).first()
    
    # Get or create engagement record
    engagement = db.query(Engagement).filter(Engagement.photo_id == photo_id).first()
    if not engagement:
        engagement = Engagement(photo_id=photo_id, likes_count=0)
        db.add(engagement)
        db.commit()
        db.refresh(engagement)
    
    if existing_like:
        # Unlike: remove like and decrement count
        db.delete(existing_like)
        engagement.likes_count = max(0, engagement.likes_count - 1)
        liked = False
    else:
        # Like: add like and increment count
        new_like = Like(photo_id=photo_id, user_id=user_id)
        db.add(new_like)
        engagement.likes_count += 1
        liked = True
    
    db.commit()
    db.refresh(engagement)
    
    # Broadcast like count update via WebSocket
    from app.websockets.broadcast import broadcast_like_update
    broadcast_like_update(
        photo_id=photo_id,
        likes_count=engagement.likes_count,
        liked=liked,
        user_id=user_id
    )
    
    return {
        "photo_id": photo_id,
        "user_id": user_id,
        "liked": liked,
        "likes_count": engagement.likes_count
    }


def create_comment(db: Session, photo_id: int, user_id: int, comment: CommentCreate) -> Comment:
    """Create a new comment on a photo."""
    # Get or create engagement record
    engagement = db.query(Engagement).filter(Engagement.photo_id == photo_id).first()
    if not engagement:
        engagement = Engagement(photo_id=photo_id, likes_count=0)
        db.add(engagement)
        db.commit()
        db.refresh(engagement)
    
    # Create comment
    db_comment = Comment(
        engagement_id=engagement.id,
        author_id=user_id,
        content=comment.content,
        parent_id=comment.parent_id
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments_by_photo(db: Session, photo_id: int) -> List[Comment]:
    """Get all comments for a photo, organized in threads."""
    engagement = db.query(Engagement).filter(Engagement.photo_id == photo_id).first()
    if not engagement:
        return []
    
    # Get all comments for this engagement
    comments = db.query(Comment).filter(
        Comment.engagement_id == engagement.id
    ).order_by(Comment.created_at).all()
    
    return comments


def get_user_liked_photos(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Photo]:
    """Get all photos liked by a user."""
    photos = db.query(Photo).join(Like).filter(
        Like.user_id == user_id
    ).offset(skip).limit(limit).all()
    return photos


def get_user_tagged_photos(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Photo]:
    """Get all photos where user is tagged."""
    photos = db.query(Photo).join(TaggedIn).filter(
        TaggedIn.user_id == user_id
    ).offset(skip).limit(limit).all()
    return photos


def tag_user_in_photo(db: Session, photo_id: int, user_id: int) -> TaggedIn:
    """Tag a user in a photo."""
    # Check if already tagged
    existing_tag = db.query(TaggedIn).filter(
        TaggedIn.photo_id == photo_id,
        TaggedIn.user_id == user_id
    ).first()
    
    if existing_tag:
        return existing_tag
    
    # Create new tag
    tagged = TaggedIn(photo_id=photo_id, user_id=user_id)
    db.add(tagged)
    db.commit()
    db.refresh(tagged)
    return tagged

