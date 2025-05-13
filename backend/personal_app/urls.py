from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InterestTagViewSet, CommunityViewSet, PostViewSet, CommentViewSet,
    CommunityCreationRequestViewSet, PersonalPostViewSet, FollowViewSet,
    UserFeedView # Added UserFeedView
)

router = DefaultRouter()
router.register(r"interest-tags", InterestTagViewSet, basename="interesttag")
router.register(r"communities", CommunityViewSet, basename="community")
router.register(r"posts", PostViewSet, basename="post") # For community posts
router.register(r"comments", CommentViewSet, basename="comment")
router.register(r"community-requests", CommunityCreationRequestViewSet, basename="communitycreationrequest")
router.register(r"personal-posts", PersonalPostViewSet, basename="personalpost") # For individual user posts (not feed)
router.register(r"follows", FollowViewSet, basename="follow")

urlpatterns = [
    path("", include(router.urls)),
    path("feed/", UserFeedView.as_view(), name="user-feed"), # Added URL for the feed
]

