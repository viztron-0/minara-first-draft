from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import (
    InterestTag, Community, CommunityMembership, Post, Comment, Vote,
    CommunityCreationRequest, PersonalPost, Follow
)
from .serializers import (
    InterestTagSerializer, CommunitySerializer, CommunityMembershipSerializer,
    PostSerializer, CommentSerializer, VoteSerializer,
    CommunityCreationRequestSerializer, PersonalPostSerializer, FollowSerializer
)
from .permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly, IsCommunityAdminOrMemberReadOnly

from django.conf import settings
from django.contrib.auth import get_user_model # Use get_user_model
User = get_user_model()

class InterestTagViewSet(viewsets.ModelViewSet):
    queryset = InterestTag.objects.all()
    serializer_class = InterestTagSerializer
    permission_classes = [permissions.IsAdminUser]

class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    # Adjusted permissions: Authenticated users can create, others can read.
    # Specific object permissions (like IsCommunityAdminOrMemberReadOnly) can be added for update/delete.
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action in ["update", "partial_update", "destroy"]:
            # Apply stricter permissions for modification, e.g., only admin or community creator/admin
            self.permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly] # Or a custom IsCommunityOwnerOrAdmin
        else:
            self.permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def join(self, request, pk=None):
        community = self.get_object()
        user = request.user
        membership, created = CommunityMembership.objects.get_or_create(
            user=user, 
            community=community,
            defaults={"is_approved": not community.requires_approval}
        )
        if not created and not membership.is_approved and community.requires_approval:
            return Response({"detail": "Request to join is pending approval."}, status=status.HTTP_400_BAD_REQUEST)
        if not created and membership.is_approved:
            return Response({"detail": "Already a member."}, status=status.HTTP_400_BAD_REQUEST)
        
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        message = "Successfully joined community." if membership.is_approved else "Request to join community submitted."
        return Response({"detail": message, "membership_id": membership.id, "is_approved": membership.is_approved}, status=status_code)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def leave(self, request, pk=None):
        community = self.get_object()
        user = request.user
        try:
            membership = CommunityMembership.objects.get(user=user, community=community)
            membership.delete()
            return Response({"detail": "Successfully left community."}, status=status.HTTP_204_NO_CONTENT)
        except CommunityMembership.DoesNotExist:
            return Response({"detail": "Not a member of this community."}, status=status.HTTP_400_BAD_REQUEST)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        community_id = self.request.query_params.get("community_id")
        if community_id:
            queryset = queryset.filter(community_id=community_id)
        return queryset

    def perform_create(self, serializer):
        community_id = self.request.data.get("community")
        community = get_object_or_404(Community, pk=community_id)
        # Ensure user is a member of the community to post (or admin)
        # For MVP, assuming if they can see the community, they can attempt to post.
        # More granular checks can be added via IsCommunityAdminOrMemberReadOnly or similar.
        serializer.save(author=self.request.user, community=community)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def vote(self, request, pk=None):
        post = self.get_object()
        vote_type = request.data.get("vote_type")
        if vote_type not in [1, -1]:
            return Response({"detail": "Invalid vote type."}, status=status.HTTP_400_BAD_REQUEST)
        
        vote_data = {"post": post.pk, "vote_type": vote_type}
        serializer = VoteSerializer(data=vote_data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by("created_at")
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        post_id = self.request.query_params.get("post_id")
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset.filter(parent_comment__isnull=True)

    def perform_create(self, serializer):
        post_id = self.request.data.get("post")
        post = get_object_or_404(Post, pk=post_id)
        parent_comment_id = self.request.data.get("parent_comment")
        parent_comment = None
        if parent_comment_id:
            parent_comment = get_object_or_404(Comment, pk=parent_comment_id)
        serializer.save(author=self.request.user, post=post, parent_comment=parent_comment)

class CommunityCreationRequestViewSet(viewsets.ModelViewSet):
    queryset = CommunityCreationRequest.objects.all()
    serializer_class = CommunityCreationRequestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(requested_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(requested_by=self.request.user)
    
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        req = self.get_object()
        if req.status == "PENDING":
            Community.objects.create(name=req.name, description=req.description, created_by=req.requested_by)
            req.status = "APPROVED"
            req.admin_notes = request.data.get("admin_notes", "Approved by admin.")
            req.save()
            return Response({"detail": "Request approved and community created."}, status=status.HTTP_200_OK)
        return Response({"detail": "Request not pending."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        req = self.get_object()
        if req.status == "PENDING":
            req.status = "REJECTED"
            req.admin_notes = request.data.get("admin_notes", "Rejected by admin.")
            req.save()
            return Response({"detail": "Request rejected."}, status=status.HTTP_200_OK)
        return Response({"detail": "Request not pending."}, status=status.HTTP_400_BAD_REQUEST)

class PersonalPostViewSet(viewsets.ModelViewSet):
    queryset = PersonalPost.objects.all().order_by("-created_at")
    serializer_class = PersonalPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get("user_id")
        if user_id:
            return queryset.filter(author_id=user_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class UserFeedView(generics.ListAPIView):
    serializer_class = PersonalPostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        followed_users = Follow.objects.filter(follower=user).values_list("followed_id", flat=True)
        return PersonalPost.objects.filter(author_id__in=list(followed_users)).order_by("-created_at")

class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        list_type = self.request.query_params.get("type", "following")
        if list_type == "following":
            return super().get_queryset().filter(follower=self.request.user)
        elif list_type == "followers":
            return super().get_queryset().filter(followed=self.request.user)
        return Follow.objects.none()

    def perform_create(self, serializer):
        followed_user = serializer.validated_data.get("followed")
        if self.request.user == followed_user:
            from rest_framework import serializers # Import serializers for ValidationError
            raise serializers.ValidationError({"detail": "You cannot follow yourself."})
        serializer.save(follower=self.request.user)

    @action(detail=False, methods=["delete"], url_path="unfollow/(?P<followed_user_id>[^/.]+)")
    def unfollow(self, request, followed_user_id=None):
        follower = request.user
        followed = get_object_or_404(User, pk=followed_user_id)
        try:
            follow_instance = Follow.objects.get(follower=follower, followed=followed)
            follow_instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response({"detail": "Not following this user."}, status=status.HTTP_404_NOT_FOUND)

