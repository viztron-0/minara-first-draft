from django.db import models
from django.conf import settings

# Using the custom User model from the 'users' app
User = settings.AUTH_USER_MODEL

class InterestTag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, help_text="A short label for URLs, e.g., theological-discussion")

    def __str__(self):
        return self.name

class Community(models.Model):
    # Basic Info
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_communities")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=False, help_text="Private communities require approval to join")
    requires_approval = models.BooleanField(default=False, help_text="If true, admins must approve new members (even if public)")

    # Location-based fields (can be normalized further if needed)
    region = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    state_province = models.CharField(max_length=100, blank=True, null=True, verbose_name="State/Province")
    city = models.CharField(max_length=100, blank=True, null=True)

    # Age Group (simplified for MVP, could be more granular)
    AGE_GROUPS = [
        ("18-25", "18-25"),
        ("25-45", "25-45"),
        ("45-80", "45-80"),
        ("ALL", "All Ages"), # Default or for general communities
    ]
    target_age_group = models.CharField(max_length=10, choices=AGE_GROUPS, default="ALL", blank=True, null=True)

    # Gender Specific (simplified for MVP)
    GENDER_SPECIFICITY = [
        ("M", "Male Only"),
        ("F", "Female Only"),
        ("ALL", "All Genders"), # Default
    ]
    gender_specificity = models.CharField(max_length=3, choices=GENDER_SPECIFICITY, default="ALL", blank=True, null=True)

    # Interest-based
    interests = models.ManyToManyField(InterestTag, blank=True, related_name="communities")

    # Members
    members = models.ManyToManyField(User, through="CommunityMembership", related_name="joined_communities")
    admins = models.ManyToManyField(User, related_name="administered_communities", blank=True)

    # Profile picture/icon for the community
    profile_image_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk and self.created_by and not self.admins.exists():
            # Automatically add creator as an admin on creation if no admins are set
            # This needs to be done after the initial save due to M2M relationship
            super().save(*args, **kwargs)
            self.admins.add(self.created_by)
        else:
            super().save(*args, **kwargs)

class CommunityMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    community = models.ForeignKey(Community, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False, help_text="True if member request is approved")
    # Role can be added later (e.g., member, moderator)

    class Meta:
        unique_together = ("user", "community")

    def __str__(self):
        return f"{self.user.email} in {self.community.name}"

class Post(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=255)
    content = models.TextField()
    # For MVP, text-based. Later can add image, video, link fields.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    upvotes_count = models.IntegerField(default=0) # Denormalized for quick sorting, update with signals/tasks

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_comment = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")

    def __str__(self):
        return f"Comment by {self.author.email} on {self.post.title}"

class Vote(models.Model):
    VOTE_CHOICES = [
        (1, "Upvote"),
        (-1, "Downvote"), # If downvoting is a feature
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="votes")
    vote_type = models.SmallIntegerField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post") # User can only vote once per post

    def __str__(self):
        return f"{self.user.email} voted on {self.post.title}"

# Model for user requests to create a public group (community)
class CommunityCreationRequest(models.Model):
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    reason = models.TextField(blank=True, help_text="Reason for requesting this community")
    # Location, Age, Gender, Interests can be added if needed for request details
    requested_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    admin_notes = models.TextField(blank=True, help_text="Notes from admin regarding the request")

    def __str__(self):
        return f"Request for {self.name} by {self.requested_by.email}"

# Personal Feed Posts (akin to Instagram posts, distinct from community posts)
class PersonalPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="personal_posts")
    content = models.TextField()
    image_url = models.URLField(max_length=500, blank=True, null=True) # For image posts
    # video_url = models.URLField(max_length=500, blank=True, null=True) # Future
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Personal post by {self.author.email} at {self.created_at}"

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name="followers", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "followed")

    def __str__(self):
        return f"{self.follower.email} follows {self.followed.email}"

