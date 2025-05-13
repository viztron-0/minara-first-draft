from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class ChatRoom(models.Model):
    """A chat room for 1-to-1 or group messages."""
    name = models.CharField(max_length=255, blank=True, null=True, help_text="Optional name for group chats")
    # For 1-to-1 chats, participants list is enough. For group chats, name can be set.
    # For community-linked chats, this could link to a Community model instance.
    # community = models.ForeignKey("personal_app.Community", on_delete=models.SET_NULL, null=True, blank=True, related_name="chat_room")
    
    participants = models.ManyToManyField(User, related_name="chat_rooms")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.name:
            return self.name
        # For 1-to-1 chats, generate a name from participants (can be complex if many participants)
        # This is a simplified representation for __str__
        return f"Chat between {', '.join([user.email for user in self.participants.all()[:2]])}"

class Message(models.Model):
    """A message within a chat room."""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    # read_by = models.ManyToManyField(User, related_name="read_messages", blank=True) # For read receipts, future enhancement

    def __str__(self):
        return f"Message from {self.sender.email} in {self.room.name if self.room.name else '1-to-1 chat'} at {self.timestamp}"

    class Meta:
        ordering = ["timestamp"]

# Voice call functionality is complex for MVP backend via simple Django models.
# It would typically involve WebRTC and signaling servers.
# For MVP, we might just log call attempts or statuses if P2P is handled client-side with signaling.
# For now, focusing on text chat. Voice call feature will be noted as needing more infra.

