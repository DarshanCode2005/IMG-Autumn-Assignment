from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import require_admin_or_coordinator
from app.crud import event as crud_event
from app.schemas.event import Event, EventCreate, EventUpdate
from app.models.models import User

router = APIRouter(prefix="/events", tags=["events"])


@router.post("/", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_event(
    event: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator)
):
    """Create a new event. Restricted to Admin and Coordinator."""
    return crud_event.create_event(db=db, event=event)


@router.get("/", response_model=List[Event])
def read_events(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all events with pagination."""
    events = crud_event.get_events(db, skip=skip, limit=limit)
    return events


@router.get("/{event_id}", response_model=Event)
def read_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific event by ID."""
    db_event = crud_event.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return db_event


@router.get("/slug/{slug}", response_model=Event)
def read_event_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get a specific event by slug."""
    db_event = crud_event.get_event_by_slug(db, slug=slug)
    if db_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return db_event


@router.put("/{event_id}", response_model=Event)
def update_event(
    event_id: int,
    event_update: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator)
):
    """Update an event. Restricted to Admin and Coordinator."""
    db_event = crud_event.update_event(db, event_id=event_id, event_update=event_update)
    if db_event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return db_event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_coordinator)
):
    """Delete an event. Restricted to Admin and Coordinator."""
    success = crud_event.delete_event(db, event_id=event_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    return None

