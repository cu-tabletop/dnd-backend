from django.urls import path
from .views import *

urlpatterns = [
    path('ping/', ping, name="ping"),
    path('upload/character/', upload_character, name="upload character"),
    path('character/get/', get_character_view, name='get character'),
]