from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.websockets.manager import manager
import json

router = APIRouter()


@router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    """
    WebSocket endpoint for real-time notifications.
    Users receive notifications for:
    - Photo processing completion
    - Being tagged in photos
    - Likes on their photos
    """
    # For WebSocket, we need to authenticate differently
    # This is a simplified version - in production, use JWT tokens in query params
    user_id = None
    
    try:
        # Accept connection first
        await websocket.accept()
        
        # Get user_id from query params or headers
        # In production, extract from JWT token
        user_id_param = websocket.query_params.get("user_id")
        if user_id_param:
            user_id = int(user_id_param)
        else:
            # For now, reject if no user_id
            await websocket.close(code=1008, reason="Authentication required")
            return
        
        # Connect to manager
        await manager.connect(websocket, user_id)
        
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to notifications",
            "user_id": user_id
        })
        
        # Keep connection alive and listen for messages
        while True:
            # Wait for any incoming messages (ping/pong, etc.)
            try:
                data = await websocket.receive_text()
                # Echo back or handle client messages
                await websocket.send_json({
                    "type": "echo",
                    "message": "Received",
                    "data": data
                })
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        if user_id:
            await manager.disconnect(websocket)


@router.websocket("/ws/gallery/{photo_id}")
async def websocket_gallery_updates(websocket: WebSocket, photo_id: int):
    """
    WebSocket endpoint for live gallery updates.
    Broadcasts like count changes for a specific photo.
    Clients can connect to this endpoint to receive real-time updates.
    """
    user_id = None
    try:
        await websocket.accept()
        
        # Get user_id from query params (optional)
        user_id_param = websocket.query_params.get("user_id")
        user_id = int(user_id_param) if user_id_param else None
        
        # Connect to manager if user_id provided
        if user_id:
            await manager.connect(websocket, user_id)
        
        # Send initial photo data
        db = SessionLocal()
        try:
            from app.crud.photo import get_photo
            from app.models.models import Engagement
            photo = get_photo(db, photo_id)
            
            if photo:
                engagement = db.query(Engagement).filter(Engagement.photo_id == photo_id).first()
                likes_count = engagement.likes_count if engagement else 0
                
                await websocket.send_json({
                    "type": "photo_update",
                    "photo_id": photo_id,
                    "likes_count": likes_count,
                    "status": "connected"
                })
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": "Photo not found"
                })
                await websocket.close()
                return
        finally:
            db.close()
        
        # Keep connection alive and listen for updates
        # The manager will send updates when likes change
        while True:
            try:
                # Wait for messages (can be used for ping/pong)
                data = await websocket.receive_text()
                # Echo or handle client messages
                await websocket.send_json({
                    "type": "echo",
                    "message": "Received",
                    "data": data
                })
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Gallery WebSocket error: {e}")
                break
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Gallery WebSocket connection error: {e}")
    finally:
        if user_id:
            await manager.disconnect(websocket)
        else:
            try:
                await websocket.close()
            except:
                pass

