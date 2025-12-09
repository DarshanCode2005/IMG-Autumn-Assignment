from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean, Text, JSON, DateTime
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship
from datetime import date, datetime
from app.models.base import Base


class User(Base):
    """User model with authentication and role-based access."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # Admin, Coordinator, Photographer, Member, Guest
    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False)
    photos = relationship("Photo", back_populates="uploader", foreign_keys="Photo.uploader_id")
    comments = relationship("Comment", back_populates="author")
    likes = relationship("Like", back_populates="user")
    tagged_in = relationship("TaggedIn", back_populates="user")


class Profile(Base):
    """User profile information."""
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    batch = Column(String, nullable=True)
    dept = Column(String, nullable=True)
    profile_pic = Column(String, nullable=True)  # Path to profile picture

    # Relationships
    user = relationship("User", back_populates="profile")


class Event(Base):
    """Event model for organizing photos."""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, index=True, nullable=False)
    date = Column(Date, nullable=False)
    location = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    qr_code_path = Column(String, nullable=True)  # Path to QR code image

    # Relationships
    photos = relationship("Photo", back_populates="event", cascade="all, delete-orphan")


class Photo(Base):
    """Photo model with EXIF data and file paths."""
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    original_path = Column(String, nullable=False)
    thumbnail_path = Column(String, nullable=True)
    watermarked_path = Column(String, nullable=True)
    exif_data = Column(JSONB, nullable=True)  # PostgreSQL JSONB for EXIF data
    ai_tags = Column(JSONB, nullable=True)  # PostgreSQL JSONB for AI-generated tags
    manual_tags = Column(JSONB, nullable=True)  # PostgreSQL JSONB for user-added tags
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    uploader_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    processing_status = Column(String, default="pending", nullable=False)  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    event = relationship("Event", back_populates="photos")
    uploader = relationship("User", back_populates="photos", foreign_keys=[uploader_id])
    engagement = relationship("Engagement", back_populates="photo", uselist=False, cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="photo", cascade="all, delete-orphan")
    tagged_users = relationship("TaggedIn", back_populates="photo", cascade="all, delete-orphan")


class Engagement(Base):
    """Engagement model for likes and comments."""
    __tablename__ = "engagements"

    id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(Integer, ForeignKey("photos.id"), unique=True, nullable=False)
    likes_count = Column(Integer, default=0, nullable=False)
    extra_metadata = Column(JSONB, nullable=True)  # PostgreSQL JSONB for additional metadata

    # Relationships
    photo = relationship("Photo", back_populates="engagement")
    comments = relationship("Comment", back_populates="engagement", cascade="all, delete-orphan")


class Like(Base):
    """Individual like model for tracking user likes."""
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(Integer, ForeignKey("photos.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    photo = relationship("Photo", back_populates="likes")
    user = relationship("User", back_populates="likes")


class TaggedIn(Base):
    """Model for tracking users tagged in photos."""
    __tablename__ = "tagged_in"

    id = Column(Integer, primary_key=True, index=True)
    photo_id = Column(Integer, ForeignKey("photos.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    photo = relationship("Photo", back_populates="tagged_users")
    user = relationship("User", back_populates="tagged_in")


class Comment(Base):
    """Threaded comments model."""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    engagement_id = Column(Integer, ForeignKey("engagements.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)  # For threading
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    engagement = relationship("Engagement", back_populates="comments")
    author = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")

