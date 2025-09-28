from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from ..models import *

@api_view(['POST'])
def upload_character(request: Request):
    owner_id = request.data.get("owner_id")
    if not owner_id or not isinstance(owner_id, int):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    owner_obj = Player.objects.filter(id=owner_id)
    if not owner_obj.exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    owner_obj = owner_obj.first()

    campaign_id = request.data.get("campaign_id")
    if not campaign_id or not isinstance(campaign_id, int):
        return Response(status=status.HTTP_400_BAD_REQUEST)
    campaign_obj = Campaign.objects.filter(id=campaign_id)
    if not campaign_obj.exists():
        return Response(status=status.HTTP_404_NOT_FOUND)
    campaign_obj = campaign_obj.first()

    data = request.data.get("data")
    if not data or not isinstance(data, dict):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    char_obj = Character.objects.create(owner=owner_obj, campaign=campaign_obj)
    char_obj.save_data(data)

    return Response({
        "char_id": char_obj.id,
        "char_owner_id": char_obj.owner_id,
        "campaign_id": char_obj.campaign_id,
    }, status=status.HTTP_201_CREATED)
