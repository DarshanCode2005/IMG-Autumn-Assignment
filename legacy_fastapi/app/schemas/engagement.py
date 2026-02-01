from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class LikeResponse(BaseModel):
    photo_id: int
    user_id: int
    liked: bool
    likes_count: int

    model_config = ConfigDict(from_attributes=True)


class CommentBase(BaseModel):
    content: str
    parent_id: Optional[int] = None


class CommentCreate(CommentBase):
    pass


class Comment(CommentBase):
    id: int
    engagement_id: int
    author_id: int
    created_at: datetime
    replies: Optional[List["Comment"]] = None

    model_config = ConfigDict(from_attributes=True)


class CommentResponse(Comment):
    author_email: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Update forward reference
Comment.model_rebuild()

