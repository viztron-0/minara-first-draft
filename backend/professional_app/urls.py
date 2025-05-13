from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SkillViewSet, ProfessionalProfileViewSet, BusinessProfileViewSet, 
    JobListingViewSet, JobApplicationViewSet, FundingOpportunityViewSet, 
    FundingRequestViewSet, ProfessionalFeedPostViewSet
)

router = DefaultRouter()
router.register(r"skills", SkillViewSet, basename="skill")
router.register(r"profiles/professional", ProfessionalProfileViewSet, basename="professionalprofile")
router.register(r"profiles/business", BusinessProfileViewSet, basename="businessprofile")
router.register(r"jobs/listings", JobListingViewSet, basename="joblisting")
router.register(r"jobs/applications", JobApplicationViewSet, basename="jobapplication")
router.register(r"funding/opportunities", FundingOpportunityViewSet, basename="fundingopportunity")
router.register(r"funding/requests", FundingRequestViewSet, basename="fundingrequest")
router.register(r"feed/professional", ProfessionalFeedPostViewSet, basename="professionalfeedpost")

urlpatterns = [
    path("", include(router.urls)),
]

