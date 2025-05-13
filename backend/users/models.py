from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not phone_number:
            raise ValueError("The Phone Number field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, phone_number, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone_number"]

    def __str__(self):
        return self.email

class PersonalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="personal_profile")
    full_name = models.CharField(max_length=255, blank=True)
    profile_picture_url = models.URLField(max_length=500, blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Personal Profile"

class ProfessionalProfile(models.Model):
    # Changed related_name to avoid clash
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_core_professional_profile") 
    full_name = models.CharField(max_length=255, blank=True)
    profile_picture_url = models.URLField(max_length=500, blank=True, null=True)
    headline = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)
    work_experience_summary = models.TextField(blank=True, help_text="Summary of work experience")
    education_summary = models.TextField(blank=True, help_text="Summary of education")
    skills_summary = models.TextField(blank=True, help_text="Summary of skills")
    can_give_referrals = models.BooleanField(default=False)
    seeking_referrals = models.BooleanField(default=False) # Renamed from looking_for_referrals for consistency
    is_mentor = models.BooleanField(default=False)
    mentor_categories = models.CharField(max_length=500, blank=True, help_text="Comma-separated mentor categories/professions")
    is_mentee = models.BooleanField(default=False)
    mentee_categories = models.CharField(max_length=500, blank=True, help_text="Comma-separated mentee categories/professions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - Core Professional Profile"

class BusinessProfile(models.Model):
    # Changed related_name to avoid clash if professional_app also has a BusinessProfile linked to User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_core_business_profile") 
    company_name = models.CharField(max_length=255)
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    mission = models.TextField(blank=True)
    description = models.TextField(blank=True)
    is_startup = models.BooleanField(default=False)
    is_vc_firm = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

