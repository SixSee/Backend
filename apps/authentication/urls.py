from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import *

urlpatterns = [
    # Get user info
    path('user/', UserInfoView.as_view(), name='USER_INFO'),
    # User Signup
    path('signup/', UserSignup.as_view(), name='SIGNUP'),
    # Login for main site or app
    path('token/', UserLogin.as_view(), name='TOKEN_OBTAIN'),
    # Login of admin site only
    path('token/admin', AdminLogin.as_view(), name='ADMIN_LOGIN'),
    # JWT Token refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='TOKEN_REFRESH'),
    # Google Login Callback
    path('login/google/', GoogleLogin.as_view(), name='GOOGLE_LOGIN'),
]
