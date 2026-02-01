from pydantic import BaseModel, ConfigDict
from datetime import date as DateType
from typing import Optional


class EventBase(BaseModel):
    name: str
    date: DateType
    location: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = None
    date: Optional[DateType] = None
    location: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(extra='ignore')


class Event(EventBase):
    id: int
    slug: str
    qr_code_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class EventPublic(BaseModel):
    """Public event schema for gallery URLs."""
    id: int
    name: str
    slug: str
    date: DateType
    location: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

