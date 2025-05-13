from django.urls import path, include
from .views import UserRegistrationView, UserLoginView, PersonalProfileView # Correctly import PersonalProfileView

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user_register"),
    path("login/", UserLoginView.as_view(), name="user_login"),
    # Correctly map to PersonalProfileView for retrieve/update
    path("personal-profile/", PersonalProfileView.as_view(), name="user_personal_profile_manage"),
]

