from django.urls import path
from .views import *

urlpatterns = [
    path('ping/', ping, name="ping"),
    path('upload/character/', upload_character, name="upload character"),
]