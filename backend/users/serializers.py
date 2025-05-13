from rest_framework import serializers
from .models import User, PersonalProfile, ProfessionalProfile, BusinessProfile
from django.contrib.auth import authenticate, get_user_model

# Get the User model class
UserModel = get_user_model()

# LightUserSerializer for basic user info, to be used in other apps
class LightUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["id", "email", "phone_number"] # Adjust as needed
        read_only_fields = fields

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={"input_type": "password"})
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password", style={"input_type": "password"})

    class Meta:
        model = UserModel
        fields = ["email", "phone_number", "password", "password2"]
        extra_kwargs = {
            "phone_number": {"required": True}
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(detail={"password": "Password fields didn_t match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = UserModel.objects.create_user(**validated_data)
        PersonalProfile.objects.create(user=user)
        # ProfessionalProfile is created via its own endpoint or signal if needed
        # BusinessProfile is created via its own endpoint
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(label="Email Address")
    password = serializers.CharField(
        label="Password",
        style={"input_type": "password"},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(request=self.context.get("request"), email=email, password=password)
            if not user:
                msg = "Unable to log in with provided credentials."
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = "Must include \"email\" and \"password\"."
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs

# Detailed Profile Serializers (used within the users app for profile management if needed)
class UserPersonalProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalProfile
        fields = "__all__"
        read_only_fields = ["user"]

class UserProfessionalProfileSerializer(serializers.ModelSerializer):
    # This serializer is for the ProfessionalProfile model within the users app (if it exists there)
    # The main ProfessionalProfileSerializer is in professional_app/serializers.py
    class Meta:
        model = ProfessionalProfile # Assuming this is users.models.ProfessionalProfile
        fields = "__all__"
        read_only_fields = ["user"]

class UserBusinessProfileSerializer(serializers.ModelSerializer):
    # This serializer is for the BusinessProfile model within the users app (if it exists there)
    # The main BusinessProfileSerializer is in professional_app/serializers.py
    class Meta:
        model = BusinessProfile # Assuming this is users.models.BusinessProfile
        fields = "__all__"
        read_only_fields = ["user"]

