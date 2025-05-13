from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_framework.decorators import action # Added import for action decorator
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoomViewSet(viewsets.ModelViewSet):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.chat_rooms.all().annotate(num_participants=Count("participants")).order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["get"], url_path="messages")
    def list_messages(self, request, pk=None):
        room = self.get_object()
        if not room.participants.filter(pk=request.user.pk).exists():
            return Response({"detail": "Not authorized to access this chat room."}, status=status.HTTP_403_FORBIDDEN)
        
        messages = room.messages.all().order_by("timestamp")
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

class GetOrCreateDirectChatView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatRoomSerializer

    def post(self, request, *args, **kwargs):
        other_user_id = request.data.get("other_user_id")
        if not other_user_id:
            return Response({"detail": "other_user_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            other_user = User.objects.get(pk=other_user_id)
        except User.DoesNotExist:
            return Response({"detail": "Other user not found."}, status=status.HTTP_404_NOT_FOUND)

        current_user = request.user
        if current_user.id == other_user.id:
            return Response({"detail": "Cannot create chat with yourself."}, status=status.HTTP_400_BAD_REQUEST)

        room = ChatRoom.objects.annotate(num_participants=Count("participants"))\
                               .filter(participants=current_user)\
                               .filter(participants=other_user)\
                               .filter(num_participants=2)\
                               .filter(Q(name__isnull=True) | Q(name="") | Q(name=f"DM_{current_user.id}_{other_user.id}") | Q(name=f"DM_{other_user.id}_{current_user.id}"))\
                               .first()
        
        if room:
            serializer = self.get_serializer(room)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Create a new 1-to-1 chat room with a conventional name
            # Sort by ID to ensure consistent naming for the same pair of users
            sorted_participants_ids = sorted([current_user.id, other_user.id])
            room_name = f"DM_{sorted_participants_ids[0]}_{sorted_participants_ids[1]}"
            room = ChatRoom.objects.create(name=room_name)
            room.participants.add(current_user, other_user)
            room.save()
            serializer = self.get_serializer(room)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

