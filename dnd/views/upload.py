from django.core.files.base import ContentFile
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from ..models import *
from ..services import try_load_json
import json

@api_view(['POST'])
def upload_character(request: Request):
    owner_id = request.data.get("owner_id")
    if not owner_id or not isinstance(owner_id, int):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    owner_obj = Player.objects.filter(id=owner_id)
    if not owner_obj.exists():
        return Response(status=status.HTTP_400_BAD_REQUEST)
    owner_obj = owner_obj.first()

    data = request.data.get("data")
    if not data or not isinstance(data, dict):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    char_name = request.data.get("char_name")
    if not char_name or not isinstance(char_name, str):
        char_name = hash(char_name) % 10000

    char_obj = Character.objects.create(owner=owner_obj)
    char_obj.save_data(data)

    return Response(status=status.HTTP_201_CREATED)
