from app.core.database import SessionLocal, engine
from app.models.models import Photo
import os

def fix_paths():
    db = SessionLocal()
    try:
        photos = db.query(Photo).all()
        print(f"Checking {len(photos)} photos...")
        count = 0
        for photo in photos:
            needs_update = False
            original = photo.original_path
            thumb = photo.thumbnail_path
            
            if original and "\\" in original:
                photo.original_path = original.replace("\\", "/")
                needs_update = True
            
            if thumb and "\\" in thumb:
                photo.thumbnail_path = thumb.replace("\\", "/")
                needs_update = True
                
            if needs_update:
                count += 1
                
        db.commit()
        print(f"Fixed paths for {count} photos.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_paths()
