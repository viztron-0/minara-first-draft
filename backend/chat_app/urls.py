from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, GetOrCreateDirectChatView

router = DefaultRouter()
router.register(r"rooms", ChatRoomViewSet, basename="chatroom")
# Messages are typically accessed via the ChatRoomViewSet (e.g., /api/chat/rooms/{room_pk}/messages/)
# or handled by WebSockets directly for real-time updates.

urlpatterns = [
    path("", include(router.urls)),
    path("direct/", GetOrCreateDirectChatView.as_view(), name="get_or_create_direct_chat"),
]

