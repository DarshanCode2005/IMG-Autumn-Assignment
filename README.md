# IMG Project - Event Gallery App

A full-stack application for managing event photos with real-time engagement and AI-powered features.

## 🚀 Key Features

*   **Photo Management**: Upload original quality photos, auto-generated thumbnails, and watermarked versions.
*   **Real-time Engagement**: Live updates for **Likes** and **Comments** across all connected devices using WebSockets.
*   **AI Auto-Tagging**: Automatically generates descriptive tags for uploaded photos using a pre-trained ResNet50 model.
*   **Event Galleries**: Organize photos by events (e.g., "IMG Chaapo").
*   **Metadata Extraction**: Automatically extracts and displays EXIF data.
*   **Role-Based Access**: Coordinators and Admins have extended privileges.

## 🛠️ Tech Stack

### Backend
*   **Framework**: Django & Django REST Framework (DRF)
*   **Real-time**: Django Channels & Daphne (ASGI)
*   **Asynchronous Tasks**: Celery & Redis (Image processing, AI tagging)
*   **Database**: PostgreSQL
*   **AI/ML**: PyTorch (ResNet50)

### Mobile App
*   **Framework**: Flutter
*   **State Management**: Provider
*   **Networking**: Dio & WebSocketChannel

---

## ⚙️ Setup & Running

### 1. Backend Setup

Ensure **Redis** and **PostgreSQL** are running.

```bash
# Activate virtual environment
# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create Superuser (if needed)
python manage.py createsuperuser
```

### 2. Running the Services

To enable all features (API, WebSockets, AI), you need to run three separate processes:

**Terminal 1: ASGI Server (API + WebSockets)**
```bash
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```
*Note: Do not use `python manage.py runserver` if you want WebSockets to work properly.*

**Terminal 2: Celery Worker (AI & Image Processing)**
```bash
celery -A config worker --loglevel=info -P solo
```
*Note: Use `-P solo` or `pool=solitary` on Windows to avoid concurrency issues.*

### 3. Running the Mobile App

**Terminal 3: Flutter App**
```bash
cd mobile_app
flutter pub get
flutter run
```

---

## 📡 API Overview

*   **REST API**: `http://localhost:8000/api/v1/`
    *   `POST /auth/login/`: User login
    *   `GET /events/`: List events
    *   `GET /photos/`: List photos (with filters)
    *   `POST /photos/upload/`: Upload new photos
    *   `POST /photos/{id}/like/`: Like a photo
    *   `POST /photos/{id}/comments/`: Comment on a photo

*   **WebSockets**: `ws://localhost:8000/ws/notifications`
    *   Connect with `?user_id={id}`
    *   Receives `photo_like_update`, `new_comment`, and `photo_processed` events.

## 🧠 AI & Background Tasks

The project uses Celery to handle heavy lifting off the main thread:
1.  **Image Processing**: Generates thumbnails and adds watermarks.
2.  **EXIF Extraction**: extract metadata like Camera model, ISO, Aperture.
3.  **AI Tagging**: Loads `resnet50` to classify images and auto-assign tags (e.g., "stage", "concert", "crowd").
