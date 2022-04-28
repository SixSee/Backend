from django.urls import path

from .views import (BulletinView, SingleBulletinView, ApproveBulletinView)

urlpatterns = [
    path('', BulletinView.as_view()),
    path('<slug:slug>', SingleBulletinView.as_view()),
    path('<slug:slug>', ApproveBulletinView.as_view())
]
