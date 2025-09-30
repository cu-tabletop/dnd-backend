from io import BytesIO

from django.core.files.base import ContentFile
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import *
from rest_framework.status import *
from rest_framework.parsers import *
from rest_framework.request import Request
from rest_framework.response import Response

from ..models import *
from ..schemas.campaign import (
    create_campaign_request_schema,
    create_campaign_response_schema,
    campaign_info_response_schema,
    campaigns_list_response_schema,
    add_to_campaign_request_schema,
    add_to_campaign_response_schema,
    edit_permissions_request_schema,
    edit_permissions_response_schema,
    error_response_schema,
)

import base64
from PIL import Image as PILImage


@swagger_auto_schema(
    method="POST",
    operation_description="Create a new campaign",
    request_body=create_campaign_request_schema,
    responses={
        HTTP_201_CREATED: create_campaign_response_schema,
        HTTP_400_BAD_REQUEST: error_response_schema,
        HTTP_404_NOT_FOUND: error_response_schema,
    },
    tags=["Campaigns"],
)
@api_view(["POST"])
@parser_classes([JSONParser])
def create_campaign_view(request: Request) -> Response:
    user_id = request.data.get("telegram_id")
    if not user_id or not isinstance(user_id, int):
        return Response(status=HTTP_400_BAD_REQUEST)
    user_obj = Player.objects.filter(telegram_id=user_id)
    if not user_obj.exists():
        return Response(status=HTTP_404_NOT_FOUND)
    user_obj = user_obj.first()

    campaign_title = request.data.get("title")
    if not campaign_title or not isinstance(campaign_title, str):
        return Response(status=HTTP_400_BAD_REQUEST)

    campaign_obj = Campaign.objects.create(
        title=campaign_title,
        verified=user_obj.verified,
    )

    icon_str = request.data.get("icon")
    if icon_str and isinstance(icon_str, str):
        decoded_icon = base64.b64decode(icon_str)
        image = PILImage.open(BytesIO(decoded_icon))
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        campaign_obj.icon = ContentFile(buffer.read(), f"{campaign_title}.png")

    desc = request.data.get("description")
    if desc and isinstance(desc, str):
        campaign_obj.description = desc

    campaign_obj.save()

    CampaignMembership.objects.create(
        user=user_obj,
        campaign=campaign_obj,
        status=2,
    )
    return Response(status=HTTP_201_CREATED)


@swagger_auto_schema(
    method="GET",
    operation_description="Retrieve campaign information by ID or list accessible campaigns",
    manual_parameters=[
        openapi.Parameter(
            "campaign_id",
            openapi.IN_QUERY,
            description="ID of the campaign to retrieve (optional)",
            type=openapi.TYPE_INTEGER,
            required=False,
        ),
        openapi.Parameter(
            "user_id",
            openapi.IN_QUERY,
            description="ID of the user to filter campaigns (optional)",
            type=openapi.TYPE_INTEGER,
            required=False,
        ),
    ],
    responses={
        HTTP_200_OK: campaign_info_response_schema
        if "campaign_id" in locals()
        else campaigns_list_response_schema,
        HTTP_400_BAD_REQUEST: error_response_schema,
        HTTP_403_FORBIDDEN: error_response_schema,
        HTTP_404_NOT_FOUND: error_response_schema,
    },
    tags=["Campaigns"],
)
@api_view(["GET"])
@parser_classes([JSONParser])
def get_campaign_info_view(request: Request) -> Response:
    campaign_id = request.query_params.get("campaign_id")
    user_id = request.query_params.get("user_id")

    if campaign_id:
        try:
            campaign_obj = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            return Response(status=HTTP_404_NOT_FOUND)
        if campaign_obj.private:
            if (
                not user_id
                or not CampaignMembership.objects.filter(
                    campaign=campaign_obj, user_id=user_id
                ).exists()
            ):
                return Response(status=HTTP_403_FORBIDDEN)
        serializer = CampaignSerializer(campaign_obj)
        return Response(serializer.data, status=HTTP_200_OK)

    campaigns = Campaign.objects.filter(private=False)

    if user_id:
        try:
            user_id = int(user_id)
        except ValueError:
            return Response({"error": "Invalid user_id"}, status=HTTP_400_BAD_REQUEST)

        user_campaigns = Campaign.objects.filter(
            id__in=CampaignMembership.objects.filter(user_id=user_id).values_list(
                "campaign_id", flat=True
            )
        )
        campaigns = campaigns.union(user_campaigns)

    serializer = CampaignSerializer(campaigns, many=True)
    return Response(data={"campaigns": serializer.data}, status=HTTP_200_OK)


@swagger_auto_schema(
    method="POST",
    operation_description="Add a user to a campaign",
    request_body=add_to_campaign_request_schema,
    responses={
        HTTP_201_CREATED: add_to_campaign_response_schema,
        HTTP_200_OK: add_to_campaign_response_schema,
        HTTP_400_BAD_REQUEST: error_response_schema,
        HTTP_403_FORBIDDEN: error_response_schema,
        HTTP_404_NOT_FOUND: error_response_schema,
    },
    tags=["Campaigns"],
)
@api_view(["POST"])
@parser_classes([JSONParser])
def add_to_campaign_view(request) -> Response:
    campaign_id = request.data.get("campaign_id")
    owner_id = request.data.get("owner_id")
    user_id = request.data.get("user_id")

    if not campaign_id or not owner_id or not user_id:
        return Response(
            {"error": "Missing required parameters"}, status=HTTP_400_BAD_REQUEST
        )

    try:
        campaign_obj = Campaign.objects.get(id=campaign_id)
    except Campaign.DoesNotExist:
        return Response({"error": "Campaign not found"}, status=HTTP_404_NOT_FOUND)

    # Verify owner permissions
    if not CampaignMembership.objects.filter(
        campaign=campaign_obj, user_id=owner_id, status=2
    ).exists():
        return Response(
            {"error": "Only the owner can add members"}, status=HTTP_403_FORBIDDEN
        )

    try:
        user = Player.objects.get(id=user_id)
    except Player.DoesNotExist:
        return Response({"error": "User not found"}, status=HTTP_404_NOT_FOUND)

    membership, created = CampaignMembership.objects.get_or_create(
        user=user, campaign=campaign_obj, defaults={"status": 0}
    )
    if not created:
        membership.status = 0
        membership.save()

    return Response(
        {"message": f"User {user.id} added to campaign {campaign_obj.id}"},
        status=HTTP_201_CREATED if created else HTTP_200_OK,
    )


@swagger_auto_schema(
    methods=["POST", "PUT"],
    operation_description="Edit user permissions in a campaign",
    request_body=edit_permissions_request_schema,
    responses={
        HTTP_200_OK: edit_permissions_response_schema,
        HTTP_400_BAD_REQUEST: error_response_schema,
        HTTP_403_FORBIDDEN: error_response_schema,
        HTTP_404_NOT_FOUND: error_response_schema,
    },
    tags=["Campaigns"],
)
@api_view(["POST", "PUT"])
@parser_classes([JSONParser])
def edit_permissions_view(request) -> Response:
    campaign_id = request.data.get("campaign_id")
    owner_id = request.data.get("owner_id")
    user_id = request.data.get("user_id")
    new_status = request.data.get("status")  # 0 - player, 1 - master, 2 - owner

    if not all([campaign_id, owner_id, user_id]) or new_status is None:
        return Response(
            {"error": "Missing required parameters"}, status=HTTP_400_BAD_REQUEST
        )

    if new_status not in [0, 1, 2]:
        return Response({"error": "Invalid status value"}, status=HTTP_400_BAD_REQUEST)

    try:
        campaign = Campaign.objects.get(id=campaign_id)
    except Campaign.DoesNotExist:
        return Response({"error": "Campaign not found"}, status=HTTP_404_NOT_FOUND)

    # Verify owner permissions
    if not CampaignMembership.objects.filter(
        campaign=campaign, user_id=owner_id, status=2
    ).exists():
        return Response(
            {"error": "Only the owner can edit permissions"}, status=HTTP_403_FORBIDDEN
        )

    try:
        membership = CampaignMembership.objects.get(campaign=campaign, user_id=user_id)
    except CampaignMembership.DoesNotExist:
        return Response({"error": "Membership not found"}, status=HTTP_404_NOT_FOUND)

    membership.status = new_status
    membership.save()

    return Response(
        {
            "message": f"Updated user {user_id} role to {new_status} in campaign {campaign.id}"
        },
        status=HTTP_200_OK,
    )
