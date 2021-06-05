
from django.urls import path

from . import views

urlpatterns = [
    path('wix-install', views.installWix, name="installWix"),
    path('wix-auth', views.authWix, name="authWix"),
]
