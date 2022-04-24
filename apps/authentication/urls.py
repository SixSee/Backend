from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import (UserInfoView, UserSignupView, AdminLoginView, AdminSignupView, UserLoginView, GoogleLoginView, MagicLinkVerifyView)

urlpatterns = [
    # Get user info
    path('user/', UserInfoView.as_view(), name='USER_INFO'),
    # User Signup
    path('signup/', UserSignupView.as_view(), name='SIGNUP'),
    # Login for main site or app
    path('token/', UserLoginView.as_view(), name='TOKEN_OBTAIN'),
    # Login of admin site only
    path('admin/token/', AdminLoginView.as_view(), name='ADMIN_LOGIN'),
    # Admin Signup
    path('admin/signup/', AdminSignupView.as_view(), name='SIGNUP'),
    # JWT Token refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='TOKEN_REFRESH'),
    # Google Login Callback
    path('login/google/', GoogleLoginView.as_view(), name='GOOGLE_LOGIN'),

    path('magic-link/', MagicLinkVerifyView.as_view())
]
