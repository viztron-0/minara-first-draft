from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model # Import get_user_model

User = get_user_model() # Use get_user_model to get the actual User model class

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class ProfessionalProfile(models.Model):
    # Changed related_name to avoid clash
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_detailed_professional_profile") 
    headline = models.CharField(max_length=255, blank=True)
    summary = models.TextField(blank=True)
    work_experience = models.JSONField(default=list, blank=True, help_text="List of work experiences, e.g., [{\"title\": \"Engineer\", \"company\": \"Acme\"}]")
    education = models.JSONField(default=list, blank=True, help_text="List of education entries, e.g., [{\"degree\": \"BSc\", \"school\": \"State U\"}]")
    skills = models.ManyToManyField(Skill, blank=True, related_name="professional_profiles")
    resume_url = models.URLField(max_length=500, blank=True, null=True)
    can_give_referrals = models.BooleanField(default=False)
    looking_for_referrals = models.BooleanField(default=False)
    is_mentor = models.BooleanField(default=False)
    mentor_professions = models.CharField(max_length=255, blank=True, help_text="Comma-separated list of professions for mentorship")
    is_mentee = models.BooleanField(default=False)
    mentee_professions = models.CharField(max_length=255, blank=True, help_text="Comma-separated list of professions for mentee interest")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Detailed Professional Profile for {self.user.email}"

class BusinessProfile(models.Model):
    user_manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name="managed_business_profiles")
    company_name = models.CharField(max_length=255, unique=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(max_length=50, blank=True, help_text="e.g., 1-10 employees, 50-200 employees")
    website_url = models.URLField(max_length=500, blank=True, null=True)
    logo_url = models.URLField(max_length=500, blank=True, null=True)
    mission_statement = models.TextField(blank=True)
    is_startup = models.BooleanField(default=False)
    is_vc_firm = models.BooleanField(default=False, verbose_name="Is Venture Capital Firm")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

class JobListing(models.Model):
    posted_by_business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name="job_listings")
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    EMPLOYMENT_TYPE_CHOICES = [
        ("FULL_TIME", "Full-time"),
        ("PART_TIME", "Part-time"),
        ("CONTRACT", "Contract"),
        ("INTERNSHIP", "Internship"),
        ("TEMPORARY", "Temporary"),
    ]
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, blank=True)
    required_skills = models.ManyToManyField(Skill, blank=True, related_name="job_listings")
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} at {self.posted_by_business.company_name}"

class JobApplication(models.Model):
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="job_applications")
    job_listing = models.ForeignKey(JobListing, on_delete=models.CASCADE, related_name="applications")
    application_date = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ("APPLIED", "Applied"),
        ("UNDER_REVIEW", "Under Review"),
        ("INTERVIEWING", "Interviewing"),
        ("OFFERED", "Offered"),
        ("REJECTED", "Rejected"),
        ("WITHDRAWN", "Withdrawn"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="APPLIED")
    cover_letter = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("applicant", "job_listing")

    def __str__(self):
        return f"Application by {self.applicant.email} for {self.job_listing.title}"

class FundingOpportunity(models.Model):
    posted_by_business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name="funding_opportunities")
    title = models.CharField(max_length=255)
    description = models.TextField()
    funding_amount_range = models.CharField(max_length=100, blank=True, help_text="e.g., $50k - $250k")
    eligibility_criteria = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Funding: {self.title} by {self.posted_by_business.company_name}"

class FundingRequest(models.Model):
    requested_by_business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name="funding_requests")
    title = models.CharField(max_length=255)
    description = models.TextField()
    funding_amount_sought = models.CharField(max_length=100, blank=True, help_text="e.g., $100k")
    business_plan_url = models.URLField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Funding Request: {self.title} by {self.requested_by_business.company_name}"

class ProfessionalFeedPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="professional_feed_posts")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Professional post by {self.author.email} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

