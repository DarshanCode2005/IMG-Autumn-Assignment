# IMG Project

FastAPI application for image management with PostgreSQL, Redis, and Celery.

## Project Structure

```
app/
├── api/          # API routes
├── core/         # Core configuration and database
├── models/       # SQLAlchemy models
├── schemas/      # Pydantic schemas
├── crud/         # CRUD operations
├── worker/       # Celery worker tasks
└── websockets/   # WebSocket handlers
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start services with Docker Compose:
```bash
docker-compose up -d
```

3. Run the application:
```bash
uvicorn main:app --reload
```

## Services

- **FastAPI**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **Celery Worker**: Running in Docker container

## Database Models

- **Users**: Authentication and role-based access
- **Profile**: User profile information
- **Events**: Event organization
- **Photos**: Photo storage with EXIF data (JSONB)
- **Engagement**: Likes and comments
- **Comments**: Threaded comments

