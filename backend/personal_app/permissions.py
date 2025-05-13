from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit an object.
    Assumes the model instance has an `created_by` attribute.
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS requests to anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the admin users.
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS requests to anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions are only allowed to the admin users or the creator of the community.
        # For Community, creator is obj.created_by
        # This can be made more generic if needed.
        if hasattr(obj, "created_by"):
            return request.user and (request.user.is_staff or obj.created_by == request.user)
        return request.user and request.user.is_staff

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow authors of an object to edit it.
    Assumes the model instance has an `author` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we_ll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the post/comment.
        return obj.author == request.user or (request.user and request.user.is_staff)

class IsCommunityAdminOrMemberReadOnly(permissions.BasePermission):
    """
    Custom permission for community-specific actions.
    - Read-only for members.
    - Write access for community admins.
    """
    def has_object_permission(self, request, view, obj):
        # obj is the Community instance
        if request.method in permissions.SAFE_METHODS:
            # Check if user is a member for read access (if community is private)
            if obj.is_private:
                return obj.members.filter(id=request.user.id).exists() or request.user in obj.admins.all() or (request.user and request.user.is_staff)
            return True # Public communities are readable by anyone

        # Write permissions are only allowed to community admins or site staff.
        return request.user in obj.admins.all() or (request.user and request.user.is_staff)

