from django.urls import path
from .views import acceuil

urlpatterns = [
    path("", acceuil, name="acceuil"),
]