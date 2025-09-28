from io import BytesIO

from django.core.files.base import ContentFile
from rest_framework.decorators import *
from rest_framework.status import *
from rest_framework.parsers import *
from rest_framework.request import Request
from rest_framework.response import Response

from ..models import *

import base64
from PIL import Image as PILImage

@api_view(['POST'])
@parser_classes([JSONParser])
def create_campaign_view(request: Request) -> Response:
    user_id = request.data.get('telegram_id')
    if not user_id or not isinstance(user_id, int):
        return Response(status=HTTP_400_BAD_REQUEST)
    user_obj = Player.objects.filter(telegram_id=user_id)
    if not user_obj.exists():
        return Response(status=HTTP_404_NOT_FOUND)
    user_obj = user_obj.first()

    campaign_title = request.data.get('title')
    if not campaign_title or not isinstance(campaign_title, str):
        return Response(status=HTTP_400_BAD_REQUEST)

    campaign_obj = Campaign.objects.create(
        title=campaign_title,
        verified=user_obj.verified,
    )

    icon_str = request.data.get('icon')
    if icon_str and isinstance(icon_str, str):
        decoded_icon = base64.b64decode(icon_str)
        image = PILImage.open(BytesIO(decoded_icon))
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        campaign_obj.icon = ContentFile(buffer.read(), f"{campaign_title}.png")

    desc = request.data.get('description')
    if desc and isinstance(desc, str):
        campaign_obj.description = desc

    campaign_obj.save()

    CampaignMembership.objects.create(
        user=user_obj,
        campaign=campaign_obj,
        status=2,
    )
    return Response(status=HTTP_201_CREATED)

@api_view(['GET'])
@parser_classes([JSONParser])
def get_campaign_info_view(request: Request) -> Response:

    return Response(data={}, status=HTTP_200_OK)

@api_view(['GET'])
@parser_classes([JSONParser])
def add_master_to_campaign_view(request: Request) -> Response:

    return Response(data={}, status=HTTP_200_OK)

@api_view(['GET'])
@parser_classes([JSONParser])
def edit_permissions_view(request: Request) -> Response:

    return Response(data={}, status=HTTP_200_OK)



