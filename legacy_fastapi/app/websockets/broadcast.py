"""
Helper functions for broadcasting WebSocket messages from Celery tasks.
Since Celery runs in separate processes, we need to handle async operations carefully.
"""
import asyncio
import threading
from typing import Dict, List
from app.websockets.manager import manager


def run_async_in_thread(coro):
    """Run an async coroutine in a new event loop in a separate thread."""
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(coro)
        finally:
            loop.close()
    
    thread = threading.Thread(target=run_in_thread)
    thread.daemon = True
    thread.start()


def broadcast_notification(message: Dict, user_ids: List[int] = None):
    """
    Broadcast a notification message to users.
    Can be called from Celery tasks.
    
    Args:
        message: Dictionary with notification data
        user_ids: List of user IDs to notify. If None, broadcasts to all.
    """
    if user_ids:
        coro = manager.send_to_multiple_users(message, user_ids)
    else:
        coro = manager.broadcast(message)
    
    run_async_in_thread(coro)


def broadcast_photo_processed(photo_id: int, uploader_id: int, tagged_user_ids: List[int], 
                             thumbnail_path: str = None, status: str = "completed"):
    """Broadcast photo processing completion notification."""
    message = {
        "type": "photo_processed",
        "photo_id": photo_id,
        "status": status,
        "thumbnail_path": thumbnail_path,
        "message": "Your photo has been processed successfully" if status == "completed" else "Photo processing failed"
    }
    
    user_ids = [uploader_id] + tagged_user_ids
    broadcast_notification(message, user_ids)


def broadcast_like_update(photo_id: int, likes_count: int, liked: bool, user_id: int):
    """Broadcast like count update to all connected users."""
    message = {
        "type": "like_update",
        "photo_id": photo_id,
        "likes_count": likes_count,
        "liked": liked,
        "user_id": user_id
    }
    
    # Broadcast to all connected users
    # In production, you could track which users are viewing which photos
    # and only send to those users for better performance
    broadcast_notification(message)

