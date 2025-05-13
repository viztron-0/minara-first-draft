from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, PersonalProfile, ProfessionalProfile, BusinessProfile
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer,
    UserPersonalProfileSerializer, # Renamed from PersonalProfileSerializer
    UserProfessionalProfileSerializer, # Renamed from ProfessionalProfileSerializer
    UserBusinessProfileSerializer # Renamed from BusinessProfileSerializer
)

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny] # Anyone can register

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "user": UserRegistrationSerializer(user).data, # Use UserRegistrationSerializer for user data
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny] # Anyone can attempt to log in

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response({
            "email": user.email,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "Login successful."
        }, status=status.HTTP_200_OK)

class PersonalProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserPersonalProfileSerializer # Renamed
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = PersonalProfile.objects.get_or_create(user=self.request.user)
        return profile

class ProfessionalProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfessionalProfileSerializer # Renamed
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # ProfessionalProfile in users.models is the one linked to the User model directly.
        # The one in professional_app.models is more detailed and managed by professional_app.
        # This view should manage the users.models.ProfessionalProfile.
        profile, created = ProfessionalProfile.objects.get_or_create(user=self.request.user)
        return profile

class BusinessProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserBusinessProfileSerializer # Renamed
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # This view should manage the users.models.BusinessProfile.
        # A user might manage multiple businesses via professional_app.BusinessProfile.
        # This one is for a potential primary business link directly on the user if that was the design.
        # Given the current models, users.BusinessProfile might be redundant if professional_app.BusinessProfile is the main one.
        # For now, assuming it refers to users.models.BusinessProfile.
        try:
            # If a user can only have one BusinessProfile linked directly via users.models
            return BusinessProfile.objects.get(user=self.request.user) 
        except BusinessProfile.DoesNotExist:
            from django.http import Http404
            # If it's expected that a user might not have one, and it's not created by default.
            raise Http404("Business profile not found for this user. Create one via the professional app.")

