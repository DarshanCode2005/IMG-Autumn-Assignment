from app.core.database import SessionLocal
from app.models.models import Photo, User
import os

def test_db():
    db = SessionLocal()
    try:
        user = db.query(User).first()
        if not user:
            print("No users found. Creating a dummy user...")
            from app.core.security import get_password_hash
            user = User(email="dummy@test.com", password=get_password_hash("password"), role="Admin")
            db.add(user)
            db.commit()
            db.refresh(user)
        
        photo = Photo(
            original_path="media/originals/test.jpg",
            uploader_id=user.id,
            processing_status="completed"
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)
        print(f"Direct photo creation success. ID: {photo.id}")
        
        count = db.query(Photo).count()
        print(f"Total photos in DB: {count}")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_db()
