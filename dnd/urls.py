from django.urls import path
from .views import *

urlpatterns = [
    path('ping/', ping, name="ping"),
]