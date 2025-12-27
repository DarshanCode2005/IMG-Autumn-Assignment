from sqlalchemy import text
from app.core.database import engine

def migrate():
    with engine.connect() as conn:
        print("Checking for watermarked_path column...")
        try:
            # Check if column exists
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='photos' AND column_name='watermarked_path'"))
            if not result.fetchone():
                print("Adding column watermarked_path to photos table...")
                conn.execute(text("ALTER TABLE photos ADD COLUMN watermarked_path VARCHAR"))
                conn.commit()
                print("Column added successfully.")
            else:
                print("Column already exists.")
                
            print("Checking for manual_tags column...")
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='photos' AND column_name='manual_tags'"))
            if not result.fetchone():
                print("Adding column manual_tags to photos table...")
                conn.execute(text("ALTER TABLE photos ADD COLUMN manual_tags JSONB"))
                conn.commit()
                print("Column added successfully.")
            else:
                print("Column manual_tags already exists.")
        except Exception as e:
            print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
