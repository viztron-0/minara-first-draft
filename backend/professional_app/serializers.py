from rest_framework import serializers
from .models import (
    Skill, ProfessionalProfile, BusinessProfile, JobListing, 
    JobApplication, FundingOpportunity, FundingRequest, ProfessionalFeedPost
)
from users.serializers import LightUserSerializer # Ensure this import is correct and LightUserSerializer is defined in users.serializers
from django.conf import settings

User = settings.AUTH_USER_MODEL

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]

class ProfessionalProfileSerializer(serializers.ModelSerializer):
    user = LightUserSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Skill.objects.all(), source="skills", write_only=True, required=False
    )

    class Meta:
        model = ProfessionalProfile
        fields = [
            "id", "user", "headline", "summary", "work_experience", "education", 
            "skills", "skill_ids", "resume_url", "can_give_referrals", "looking_for_referrals",
            "is_mentor", "mentor_professions", "is_mentee", "mentee_professions",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def create(self, validated_data):
        # Ensure user is set from context
        validated_data["user"] = self.context["request"].user
        # Handle M2M for skills if skill_ids are passed
        skills_data = validated_data.pop("skills", None)
        profile = ProfessionalProfile.objects.create(**validated_data)
        if skills_data:
            profile.skills.set(skills_data)
        return profile
    
    def update(self, instance, validated_data):
        # Handle M2M for skills if skill_ids are passed
        if "skills" in validated_data:
            instance.skills.set(validated_data.pop("skills"))
        return super().update(instance, validated_data)

class BusinessProfileSerializer(serializers.ModelSerializer):
    user_manager = LightUserSerializer(read_only=True)

    class Meta:
        model = BusinessProfile
        fields = [
            "id", "user_manager", "company_name", "industry", "company_size", 
            "website_url", "logo_url", "mission_statement", "is_startup", "is_vc_firm",
            "created_at", "updated_at"
        ]
        read_only_fields = ["id", "user_manager", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["user_manager"] = self.context["request"].user
        return super().create(validated_data)

class JobListingSerializer(serializers.ModelSerializer):
    posted_by_business = BusinessProfileSerializer(read_only=True)
    posted_by_business_id = serializers.PrimaryKeyRelatedField(
        queryset=BusinessProfile.objects.all(), source="posted_by_business", write_only=True
    )
    required_skills = SkillSerializer(many=True, read_only=True)
    required_skill_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Skill.objects.all(), source="required_skills", write_only=True, required=False
    )
    company_name = serializers.CharField(source="posted_by_business.company_name", read_only=True)

    class Meta:
        model = JobListing
        fields = [
            "id", "posted_by_business", "posted_by_business_id", "company_name", "title", "description", "location", 
            "employment_type", "required_skills", "required_skill_ids", "is_active", "posted_at", "updated_at"
        ]
        read_only_fields = ["id", "posted_by_business", "posted_at", "updated_at", "company_name"]

    def validate_posted_by_business_id(self, value):
        if value.user_manager != self.context["request"].user and not self.context["request"].user.is_staff:
            raise serializers.ValidationError("You do not have permission to post jobs for this business.")
        return value
    
    def create(self, validated_data):
        # Handle M2M for skills if skill_ids are passed
        skills_data = validated_data.pop("required_skills", None)
        job_listing = super().create(validated_data)
        if skills_data:
            job_listing.required_skills.set(skills_data)
        return job_listing

    def update(self, instance, validated_data):
        if "required_skills" in validated_data:
            instance.required_skills.set(validated_data.pop("required_skills"))
        return super().update(instance, validated_data)

class JobApplicationSerializer(serializers.ModelSerializer):
    applicant = LightUserSerializer(read_only=True)
    job_listing_title = serializers.CharField(source="job_listing.title", read_only=True)

    class Meta:
        model = JobApplication
        fields = ["id", "applicant", "job_listing", "job_listing_title", "application_date", "status", "cover_letter"]
        read_only_fields = ["id", "applicant", "application_date", "job_listing_title"]

    def create(self, validated_data):
        validated_data["applicant"] = self.context["request"].user
        if JobApplication.objects.filter(applicant=validated_data["applicant"], job_listing=validated_data["job_listing"]).exists():
            raise serializers.ValidationError({"detail": "You have already applied for this job."})        
        return super().create(validated_data)

class FundingOpportunitySerializer(serializers.ModelSerializer):
    posted_by_business = BusinessProfileSerializer(read_only=True)
    posted_by_business_id = serializers.PrimaryKeyRelatedField(
        queryset=BusinessProfile.objects.all(), source="posted_by_business", write_only=True
    )
    company_name = serializers.CharField(source="posted_by_business.company_name", read_only=True)

    class Meta:
        model = FundingOpportunity
        fields = [
            "id", "posted_by_business", "posted_by_business_id", "company_name", "title", "description", 
            "funding_amount_range", "eligibility_criteria", "is_active", "posted_at"
        ]
        read_only_fields = ["id", "posted_by_business", "posted_at", "company_name"]

    def validate_posted_by_business_id(self, value):
        if value.user_manager != self.context["request"].user and not self.context["request"].user.is_staff:
            raise serializers.ValidationError("You do not have permission to post funding opportunities for this business.")
        return value

class FundingRequestSerializer(serializers.ModelSerializer):
    requested_by_business = BusinessProfileSerializer(read_only=True)
    requested_by_business_id = serializers.PrimaryKeyRelatedField(
        queryset=BusinessProfile.objects.all(), source="requested_by_business", write_only=True
    )
    company_name = serializers.CharField(source="requested_by_business.company_name", read_only=True)

    class Meta:
        model = FundingRequest
        fields = [
            "id", "requested_by_business", "requested_by_business_id", "company_name", "title", "description", 
            "funding_amount_sought", "business_plan_url", "is_active", "requested_at"
        ]
        read_only_fields = ["id", "requested_by_business", "requested_at", "company_name"]

    def validate_requested_by_business_id(self, value):
        if value.user_manager != self.context["request"].user and not self.context["request"].user.is_staff:
            raise serializers.ValidationError("You do not have permission to post funding requests for this business.")
        return value

class ProfessionalFeedPostSerializer(serializers.ModelSerializer):
    author = LightUserSerializer(read_only=True)

    class Meta:
        model = ProfessionalFeedPost
        fields = ["id", "author", "content", "created_at", "updated_at"]
        read_only_fields = ["id", "author", "created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

