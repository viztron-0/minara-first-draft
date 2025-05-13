import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message
from .serializers import MessageSerializer # For serializing outgoing messages

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        # Check if room exists and user is a participant (or create/add if logic allows)
        self.room = await self.get_or_create_room(self.room_name)
        if not self.room or not await self.is_user_participant(self.user, self.room):
            # More robust: check if user has permission to join/create this room_name
            # For now, if room_name is arbitrary and user is auth, let them join/create.
            # A better approach would be to have room IDs and check participation via DB.
            # This room_name could be a UUID for the ChatRoom model instance.
            # For simplicity, assuming room_name corresponds to a ChatRoom pk or a unique identifier.
            # await self.close() # Or handle room creation/joining logic here
            # return
            pass # Allow connection for now, message sending will verify participation

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        if hasattr(self, "room_group_name") and self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        if not self.user.is_authenticated:
            return # Should not happen if connect() checks auth

        text_data_json = json.loads(text_data)
        message_content = text_data_json["message"]

        # Ensure room exists and user is a participant before saving message
        if not self.room or not await self.is_user_participant(self.user, self.room):
            # Send error back to user or handle appropriately
            await self.send(text_data=json.dumps({
                "error": "You are not a participant of this room or room does not exist."
            }))
            return

        # Save message to database
        new_message = await self.save_message(self.room, self.user, message_content)
        serialized_message = await self.serialize_message(new_message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": serialized_message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))

    @database_sync_to_async
    def get_or_create_room(self, room_identifier):
        # This logic needs to be robust. room_identifier could be a ChatRoom PK or a unique name.
        # For MVP, let's assume room_identifier is the PK of an existing ChatRoom.
        # A proper system would involve creating rooms via an API and then connecting to them by ID.
        try:
            # Try to get by PK if it's an integer
            room_pk = int(room_identifier)
            room = ChatRoom.objects.filter(pk=room_pk).first()
            if room:
                 # Ensure the connecting user is a participant
                if not room.participants.filter(pk=self.user.pk).exists():
                    # If not a participant, for MVP, we might deny or add them.
                    # For now, let's assume they must be a pre-existing participant.
                    # This part of logic is crucial for security and privacy.
                    # A better approach: client gets a list of joinable rooms via API.
                    return None # Deny if not a participant
            return room
        except ValueError:
            # If room_identifier is not an int, it might be a name for a new/existing group chat
            # This part needs more thought for a production system (e.g. how are room names unique?)
            # For now, we'll simplify and assume room_identifier is a PK.
            return None 
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def is_user_participant(self, user, room):
        if not room: # if room is None from get_or_create_room
            return False
        return room.participants.filter(pk=user.pk).exists()

    @database_sync_to_async
    def save_message(self, room, sender, content):
        return Message.objects.create(room=room, sender=sender, content=content)
    
    @database_sync_to_async
    def serialize_message(self, message_obj):
        # We need a synchronous version of the serializer or pass context if serializer needs it.
        # For simplicity, let's manually construct the dict or use a simple serializer.
        # Using the serializer directly in async context can be tricky.
        # A simpler way for now:
        return {
            "id": message_obj.id,
            "room": message_obj.room.id,
            "sender": {"id": message_obj.sender.id, "email": message_obj.sender.email}, # Basic sender info
            "content": message_obj.content,
            "timestamp": message_obj.timestamp.isoformat()
        }
        # If using MessageSerializer:
        # return MessageSerializer(message_obj).data # This might cause issues with async context

