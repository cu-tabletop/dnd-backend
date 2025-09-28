from rest_framework.decorators import *
from rest_framework.status import *
from rest_framework.parsers import *
from rest_framework.request import Request
from rest_framework.response import Response

from ..models import *

@api_view(['GET'])
@parser_classes([JSONParser])
def get_character_view(request: Request) -> Response:
    try:
        char_id = int(request.query_params.get("char_id")[0]) # for some reason query params is an array
    except (ValueError, IndexError, TypeError):
        return Response(status=HTTP_400_BAD_REQUEST)
    if not char_id:
        return Response(status=HTTP_400_BAD_REQUEST)
    char_obj = Character.objects.filter(id=char_id)
    if not char_obj.exists():
        return Response(status=HTTP_404_NOT_FOUND)
    char_obj = char_obj.first()

    return Response(data={
        'char_id': char_obj.id,
        'owner_telegram_id': char_obj.owner.telegram_id,
        'char_data': char_obj.load_data(),
        'campaign_id': char_obj.campaign_id,
    }, status=HTTP_200_OK)
