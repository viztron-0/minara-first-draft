from rest_framework import serializers
from .models import ChatRoom, Message
from users.serializers import LightUserSerializer # This import should now work correctly
from django.contrib.auth import get_user_model # Import get_user_model
from django.db.models import Count # Import Count for annotation

User = get_user_model() # Use get_user_model() to get the actual User model class

class MessageSerializer(serializers.ModelSerializer):
    sender = LightUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "room", "sender", "content", "timestamp"]
        read_only_fields = ["id", "sender", "timestamp", "room"]

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = LightUserSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), source="participants", write_only=True # Now User.objects.all() will work
    )

    class Meta:
        model = ChatRoom
        fields = ["id", "name", "participants", "participant_ids", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        requesting_user = self.context["request"].user
        participants_data = validated_data.pop("participants", [])
        
        participant_instances = list(participants_data)
        if requesting_user not in participant_instances:
            participant_instances.append(requesting_user)
        
        if len(participant_instances) == 2 and not validated_data.get("name"):
            user1, user2 = participant_instances[0], participant_instances[1]
            existing_room = ChatRoom.objects.annotate(
                num_participants=Count("participants")
            ).filter(
                participants=user1
            ).filter(
                participants=user2
            ).filter(
                num_participants=2
            ).first()
            
            if existing_room:
                return existing_room

        room_name = validated_data.pop("name", None)
        if not room_name and len(participant_instances) == 2:
            sorted_participants = sorted(participant_instances, key=lambda u: u.id)
            room_name = f"DM_{sorted_participants[0].id}_{sorted_participants[1].id}"
            existing_named_room = ChatRoom.objects.filter(name=room_name).first()
            if existing_named_room:
                current_participants_set = set(p.id for p in participant_instances)
                existing_participants_set = set(p.id for p in existing_named_room.participants.all())
                if current_participants_set == existing_participants_set:
                    return existing_named_room

        room = ChatRoom.objects.create(name=room_name, **validated_data)
        room.participants.set(participant_instances)
        return room

