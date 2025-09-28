from django.urls import path
from .views import *

urlpatterns = [
    path('ping/', ping, name="ping"),
    path('character/upload/', upload_character, name="upload character"),
    path('character/get/', get_character_view, name='get character'),
    path('campaign/create/', create_campaign_view, name='create campaign'),
]