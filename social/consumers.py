import json
from channels.generic.websocket import AsyncWebsocketConsumer
from urllib.parse import parse_qs

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get user from scope (set by middleware) or from query string
        self.user = self.scope.get("user")
        
        # Also check for user_id in query string as fallback
        query_string = parse_qs(self.scope['query_string'].decode())
        user_id = query_string.get('user_id', [None])[0]
        
        if self.user and self.user.is_authenticated:
            self.group_name = f"user_{self.user.id}"
        elif user_id:
            # Allow connection with just user_id for development
            self.group_name = f"user_{user_id}"
        else:
            # Reject if no user info at all
            await self.close()
            return
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        print(f"WebSocket connected: {self.group_name}")

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
            print(f"WebSocket disconnected: {self.group_name}")

    async def notification_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['message']))
