import re
from sqlalchemy.orm import Session
from app.models.models import Event


def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from event name."""
    # Convert to lowercase and replace spaces with hyphens
    slug = name.lower().strip()
    # Remove special characters except hyphens and spaces
    slug = re.sub(r'[^\w\s-]', '', slug)
    # Replace spaces and multiple hyphens with single hyphen
    slug = re.sub(r'[-\s]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug


def get_unique_slug(db: Session, base_slug: str) -> str:
    """Generate a unique slug by appending a number if needed."""
    slug = base_slug
    counter = 1
    
    while db.query(Event).filter(Event.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    return slug

