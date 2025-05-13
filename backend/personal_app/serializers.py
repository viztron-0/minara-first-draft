from django.conf import settings
from django.contrib.auth import get_user_model # Import get_user_model
from rest_framework import serializers
from .models import (
    InterestTag, Community, CommunityMembership, Post, Comment, Vote, 
    CommunityCreationRequest, PersonalPost, Follow
)

User = get_user_model() # Get the User model class

class LightUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User # Use the actual User model class
        fields = ["id", "email", "phone_number"]

class InterestTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestTag
        fields = ["id", "name", "slug"]

class CommunityMembershipSerializer(serializers.ModelSerializer):
    user = LightUserSerializer(read_only=True)
    class Meta:
        model = CommunityMembership
        fields = ["id", "user", "community", "date_joined", "is_approved"]
        read_only_fields = ["community", "date_joined"]

class CommunitySerializer(serializers.ModelSerializer):
    created_by = LightUserSerializer(read_only=True)
    interests = InterestTagSerializer(many=True, read_only=True)
    interest_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=InterestTag.objects.all(), source="interests", write_only=True, required=False
    )
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = [
            "id", "name", "description", "created_by", "created_at", "updated_at",
            "is_private", "requires_approval", "region", "country", "state_province", "city",
            "target_age_group", "gender_specificity", "interests", "interest_ids",
            "profile_image_url", "members_count"
        ]
        read_only_fields = ["created_at", "updated_at", "created_by", "members_count"]

    def get_members_count(self, obj):
        return obj.members.count()
    
    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

class CommentSerializer(serializers.ModelSerializer):
    author = LightUserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", "post", "author", "content", "created_at", "updated_at", "parent_comment", "replies"]
        read_only_fields = ["author", "created_at", "updated_at", "post"]

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True, context=self.context).data
        return []

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

class PostSerializer(serializers.ModelSerializer):
    author = LightUserSerializer(read_only=True)
    community_name = serializers.CharField(source="community.name", read_only=True)
    comments_count = serializers.SerializerMethodField()
    upvotes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "community", "community_name", "author", "title", "content", 
            "created_at", "updated_at", "upvotes_count", "comments_count"
        ]
        read_only_fields = ["author", "created_at", "updated_at", "upvotes_count", "comments_count", "community_name"]

    def get_comments_count(self, obj):
        return obj.comments.count()

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

class VoteSerializer(serializers.ModelSerializer):
    user = LightUserSerializer(read_only=True)

    class Meta:
        model = Vote
        fields = ["id", "user", "post", "vote_type", "created_at"]
        read_only_fields = ["user", "created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        vote, created = Vote.objects.update_or_create(
            user=validated_data["user"],
            post=validated_data["post"],
            defaults={"vote_type": validated_data["vote_type"]}
        )
        post_obj = validated_data["post"]
        if created or vote.vote_type != validated_data["vote_type"]:
            upvotes = Vote.objects.filter(post=post_obj, vote_type=1).count()
            post_obj.upvotes_count = upvotes
            post_obj.save(update_fields=["upvotes_count"])
        return vote

class CommunityCreationRequestSerializer(serializers.ModelSerializer):
    requested_by = LightUserSerializer(read_only=True)

    class Meta:
        model = CommunityCreationRequest
        fields = ["id", "requested_by", "name", "description", "reason", "requested_at", "status", "admin_notes"]
        read_only_fields = ["requested_by", "requested_at", "status", "admin_notes"]

    def create(self, validated_data):
        validated_data["requested_by"] = self.context["request"].user
        return super().create(validated_data)

class PersonalPostSerializer(serializers.ModelSerializer):
    author = LightUserSerializer(read_only=True)

    class Meta:
        model = PersonalPost
        fields = ["id", "author", "content", "image_url", "created_at", "updated_at"]
        read_only_fields = ["author", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

class FollowSerializer(serializers.ModelSerializer):
    follower = LightUserSerializer(read_only=True)
    followed = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True) # Use User model directly
    followed_detail = LightUserSerializer(source="followed", read_only=True)

    class Meta:
        model = Follow
        fields = ["id", "follower", "followed", "followed_detail", "created_at"]
        read_only_fields = ["follower", "created_at", "followed_detail"]

    def create(self, validated_data):
        validated_data["follower"] = self.context["request"].user
        if validated_data["follower"] == validated_data["followed"]:
            raise serializers.ValidationError("You cannot follow yourself.")
        return super().create(validated_data)

