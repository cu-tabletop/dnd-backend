from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework.decorators import *
from rest_framework.status import *
from rest_framework.parsers import *
from rest_framework.request import Request
from rest_framework.response import Response

from ..models import *
from ..schemas.character import (
    character_response_schema,
    upload_character_request_schema,
    upload_character_response_schema,
)


@swagger_auto_schema(
    method="GET",
    operation_description="Retrieve a character by ID",
    manual_parameters=[
        openapi.Parameter(
            "char_id",
            openapi.IN_QUERY,
            description="ID of the character to retrieve",
            type=openapi.TYPE_INTEGER,
            required=True,
        ),
    ],
    responses={
        HTTP_200_OK: character_response_schema,
        HTTP_400_BAD_REQUEST: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
            description="Invalid or missing char_id",
        ),
        HTTP_404_NOT_FOUND: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
            description="Character not found",
        ),
    },
)
@api_view(["GET"])
@parser_classes([JSONParser])
def get_character_view(request: Request) -> Response:
    try:
        char_id = int(request.query_params.get("char_id"))
    except (ValueError, IndexError, TypeError):
        return Response(status=HTTP_400_BAD_REQUEST)
    if not char_id:
        return Response(status=HTTP_400_BAD_REQUEST)
    char_obj = Character.objects.filter(id=char_id)
    if not char_obj.exists():
        return Response(status=HTTP_404_NOT_FOUND)
    char_obj = char_obj.first()

    return Response(
        data={
            "char_id": char_obj.id,
            "owner_telegram_id": char_obj.owner.telegram_id,
            "char_data": char_obj.load_data(),
            "campaign_id": char_obj.campaign_id,
        },
        status=HTTP_200_OK,
    )


@swagger_auto_schema(
    method="POST",
    operation_description="Create a new character",
    request_body=upload_character_request_schema,
    responses={
        HTTP_201_CREATED: upload_character_response_schema,
        HTTP_400_BAD_REQUEST: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
            description="Invalid or missing input data",
        ),
        HTTP_404_NOT_FOUND: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"detail": openapi.Schema(type=openapi.TYPE_STRING)},
            description="Player or campaign not found",
        ),
    },
)
@api_view(["POST"])
def upload_character_view(request: Request):
    owner_id = request.data.get("owner_id")
    if not owner_id or not isinstance(owner_id, int):
        return Response(status=HTTP_400_BAD_REQUEST)
    owner_obj = Player.objects.filter(id=owner_id)
    if not owner_obj.exists():
        return Response(status=HTTP_404_NOT_FOUND)
    owner_obj = owner_obj.first()

    campaign_id = request.data.get("campaign_id")
    if not campaign_id or not isinstance(campaign_id, int):
        return Response(status=HTTP_400_BAD_REQUEST)
    campaign_obj = Campaign.objects.filter(id=campaign_id)
    if not campaign_obj.exists():
        return Response(status=HTTP_404_NOT_FOUND)
    campaign_obj = campaign_obj.first()

    data = request.data.get("data")
    if not data or not isinstance(data, dict):
        return Response(status=HTTP_400_BAD_REQUEST)

    char_obj = Character.objects.create(owner=owner_obj, campaign=campaign_obj)
    char_obj.save_data(data)

    return Response(
        {
            "char_id": char_obj.id,
            "char_owner_id": char_obj.owner_id,
            "campaign_id": char_obj.campaign_id,
        },
        status=HTTP_201_CREATED,
    )
