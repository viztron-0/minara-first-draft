from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.db.models import Q # Moved Q import to the top
from .models import (
    Skill, ProfessionalProfile, BusinessProfile, JobListing, 
    JobApplication, FundingOpportunity, FundingRequest, ProfessionalFeedPost
)
from .serializers import (
    SkillSerializer, ProfessionalProfileSerializer, BusinessProfileSerializer, 
    JobListingSerializer, JobApplicationSerializer, FundingOpportunitySerializer, 
    FundingRequestSerializer, ProfessionalFeedPostSerializer
)
# Moved IsAuthorOrReadOnly import to the top and ensured it's from the correct app
from personal_app.permissions import IsAuthorOrReadOnly 
from .permissions import IsProfileOwnerOrReadOnly, IsBusinessManagerOrReadOnly, IsJobListingOwnerOrReadOnly
from django.conf import settings
from django.contrib.auth import get_user_model # Added get_user_model import

User = get_user_model() # Use get_user_model

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAdminUser] # Only admins can create/edit skills

class ProfessionalProfileViewSet(viewsets.ModelViewSet):
    queryset = ProfessionalProfile.objects.all()
    serializer_class = ProfessionalProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsProfileOwnerOrReadOnly]

    def get_queryset(self):
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="me")
    def my_profile(self, request):
        profile, created = ProfessionalProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    @action(detail=False, methods=["put", "patch"], url_path="me/update")
    def update_my_profile(self, request):
        profile, created = ProfessionalProfile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True if request.method == "PATCH" else False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BusinessProfileViewSet(viewsets.ModelViewSet):
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsBusinessManagerOrReadOnly]

    def get_queryset(self):
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(user_manager=self.request.user)

class JobListingViewSet(viewsets.ModelViewSet):
    queryset = JobListing.objects.filter(is_active=True).order_by("-posted_at")
    serializer_class = JobListingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsJobListingOwnerOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        company_id = self.request.query_params.get("company_id")
        keyword = self.request.query_params.get("keyword")
        location = self.request.query_params.get("location")

        if company_id:
            queryset = queryset.filter(posted_by_business_id=company_id)
        if keyword:
            queryset = queryset.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))
        if location:
            queryset = queryset.filter(location__icontains=location)
        
        return queryset

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def apply(self, request, pk=None):
        job_listing = self.get_object()
        application_data = {
            "job_listing": job_listing.pk,
            "cover_letter": request.data.get("cover_letter", "")
        }
        serializer = JobApplicationSerializer(data=application_data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return JobApplication.objects.all().order_by("-application_date")
        
        managed_businesses = BusinessProfile.objects.filter(user_manager=user)
        if managed_businesses.exists():
            job_listings_for_managed_businesses = JobListing.objects.filter(posted_by_business__in=managed_businesses)
            return JobApplication.objects.filter(
                Q(applicant=user) | Q(job_listing__in=job_listings_for_managed_businesses)
            ).distinct().order_by("-application_date")
        
        return JobApplication.objects.filter(applicant=user).order_by("-application_date")

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

class FundingOpportunityViewSet(viewsets.ModelViewSet):
    queryset = FundingOpportunity.objects.filter(is_active=True).order_by("-posted_at")
    serializer_class = FundingOpportunitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsBusinessManagerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()

class FundingRequestViewSet(viewsets.ModelViewSet):
    queryset = FundingRequest.objects.filter(is_active=True).order_by("-requested_at")
    serializer_class = FundingRequestSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsBusinessManagerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save()

class ProfessionalFeedPostViewSet(viewsets.ModelViewSet):
    queryset = ProfessionalFeedPost.objects.all().order_by("-created_at")
    serializer_class = ProfessionalFeedPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

