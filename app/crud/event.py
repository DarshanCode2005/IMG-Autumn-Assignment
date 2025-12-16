import os
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.models import Event
from app.schemas.event import EventCreate, EventUpdate
from app.core.slug import generate_slug, get_unique_slug
from app.core.qrcode_generator import generate_qr_code
from app.core.config import settings


def create_event(db: Session, event: EventCreate, base_url: str = "http://localhost:8000") -> Event:
    """Create a new event with slug and QR code."""
    # Generate unique slug
    base_slug = generate_slug(event.name)
    unique_slug = get_unique_slug(db, base_slug)
    
    # Create event
    db_event = Event(
        name=event.name,
        slug=unique_slug,
        date=event.date,
        location=event.location,
        description=event.description,
    )
    
    # Generate public gallery URL
    gallery_url = f"{base_url}/events/{unique_slug}/gallery"
    
    # Generate QR code
    qr_path = generate_qr_code(gallery_url, unique_slug)
    db_event.qr_code_path = qr_path
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event


def get_event(db: Session, event_id: int) -> Optional[Event]:
    """Get event by ID."""
    return db.query(Event).filter(Event.id == event_id).first()


def get_event_by_slug(db: Session, slug: str) -> Optional[Event]:
    """Get event by slug."""
    return db.query(Event).filter(Event.slug == slug).first()


def get_events(db: Session, skip: int = 0, limit: int = 100) -> List[Event]:
    """Get all events with pagination."""
    return db.query(Event).offset(skip).limit(limit).all()


def update_event(db: Session, event_id: int, event_update: EventUpdate, base_url: str = "http://localhost:8000") -> Optional[Event]:
    """Update an event."""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        return None
    
    # Store original name to check if changed
    original_name = db_event.name
    
    # Update fields
    update_data = event_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_event, field, value)
    
    # If name changed, regenerate slug and QR code
    if "name" in update_data and update_data["name"] != original_name:
        base_slug = generate_slug(db_event.name)
        unique_slug = get_unique_slug(db, base_slug)
        db_event.slug = unique_slug
        
        # Regenerate QR code
        gallery_url = f"{base_url}/events/{unique_slug}/gallery"
        qr_path = generate_qr_code(gallery_url, unique_slug)
        db_event.qr_code_path = qr_path
    
    db.commit()
    db.refresh(db_event)
    return db_event


def delete_event(db: Session, event_id: int) -> bool:
    """Delete an event."""
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        return False
    
    # Delete QR code file if it exists
    if db_event.qr_code_path and os.path.exists(db_event.qr_code_path):
        os.remove(db_event.qr_code_path)
    
    db.delete(db_event)
    db.commit()
    return True

