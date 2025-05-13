from rest_framework import permissions

class IsProfileOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a professional profile to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the user who owns the profile.
        return obj.user == request.user or (request.user and request.user.is_staff)

class IsBusinessManagerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow managers of a business profile to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # obj is BusinessProfile, FundingOpportunity, or FundingRequest
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # For BusinessProfile itself
        if hasattr(obj, "user_manager"):
            return obj.user_manager == request.user or (request.user and request.user.is_staff)
        # For models linked to BusinessProfile (e.g., FundingOpportunity, FundingRequest)
        if hasattr(obj, "posted_by_business") and obj.posted_by_business:
            return obj.posted_by_business.user_manager == request.user or (request.user and request.user.is_staff)
        if hasattr(obj, "requested_by_business") and obj.requested_by_business:
            return obj.requested_by_business.user_manager == request.user or (request.user and request.user.is_staff)
        
        return request.user and request.user.is_staff # Fallback for safety

class IsJobListingOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the manager of the business that posted the job to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # obj is JobListing
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the manager of the business that posted the job.
        return obj.posted_by_business.user_manager == request.user or (request.user and request.user.is_staff)

# IsAuthorOrReadOnly can be reused from personal_app for ProfessionalFeedPost if the author field is consistent.
# from personal_app.permissions import IsAuthorOrReadOnly

