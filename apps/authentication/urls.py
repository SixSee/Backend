from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from .views import *

urlpatterns = [
    # User Login and Signup
    path('token/', UserLogin.as_view(), name='TOKEN_OBTAIN'),
    path('token/refresh/', TokenRefreshView.as_view(), name='TOKEN_REFRESH'),
    path('login/google/', GoogleLogin.as_view(), name='GOOGLE_LOGIN'),
    path('signup', UserSignup.as_view(), name='SIGNUP'),

    # Vendor Login and Signup
    # path('a/token', AdminLogin.as_view(), name='V_TOKEN_OBTAIN'),
    # path('a/signup', AdminSignup.as_view(), name='V_SIGNUP'),
]
