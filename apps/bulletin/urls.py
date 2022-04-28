from django.urls import path, include
from .views import (BulletinView)

urlpatterns = [
    path('', BulletinView.as_view())
]