import base64
from io import BytesIO
from typing import List

from PIL import Image as PILImage
from django.core.files.base import ContentFile
from ninja import Router, Schema
from ninja.errors import HttpError
from ninja.responses import Response

from ..models import *
from ..models.schemas import CampaignOut

router = Router()

class CreateCampaignRequest(Schema):
    telegram_id: int
    title: str
    icon: str | None = None
    description: str | None = None

@router.post("create/")
def create_campaign_view(request, campaign_request: CreateCampaignRequest) -> Response:
    user_id = campaign_request.telegram_id
    user_obj = Player.objects.filter(telegram_id=user_id)
    if not user_obj.exists():
        return Response({"message": "Target user not found"}, status=404)
    user_obj = user_obj.first()

    campaign_title = campaign_request.title

    campaign_obj = Campaign.objects.create(
        title=campaign_title,
        verified=user_obj.verified,
    )

    if campaign_request.icon:
        decoded_icon = base64.b64decode(campaign_request.icon)
        image = PILImage.open(BytesIO(decoded_icon))
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        campaign_obj.icon = ContentFile(buffer.read(), f"{campaign_title}.png")

    if campaign_request.description:
        campaign_obj.description = campaign_request.description

    campaign_obj.save()

    CampaignMembership.objects.create(
        user=user_obj,
        campaign=campaign_obj,
        status=2,
    )
    return Response({}, status=201)


@router.get("get/", response={200: CampaignOut | List[CampaignOut], 404: dict})
def get_campaign_info_view(request, campaign_id: int | None = None, user_id: int | None = None):
    if campaign_id:
        try:
            campaign_obj = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            raise HttpError(404, "requested campaign does not exist")

        if campaign_obj.private:
            if not user_id or not CampaignMembership.objects.filter(
                    campaign=campaign_obj, user_id=user_id
            ).exists():
                # 👌 disguise private campaigns as non-existent
                raise HttpError(404, "requested campaign does not exist")

        return campaign_obj

    campaigns = Campaign.objects.filter(private=False)

    if user_id:
        user_campaigns = Campaign.objects.filter(
            id__in=CampaignMembership.objects.filter(user_id=user_id)
            .values_list("campaign_id", flat=True)
        )
        campaigns = campaigns.union(user_campaigns)

    return list(campaigns)

class AddToCampaignRequest(Schema):
    campaign_id: int
    owner_id: int
    user_id: int

@router.post("add/")
def add_to_campaign_view(request, body: AddToCampaignRequest) -> Response:
    try:
        campaign_obj = Campaign.objects.get(id=body.campaign_id)
    except Campaign.DoesNotExist:
        return Response({"error": "Campaign not found"}, status=404)

    # Verify owner permissions
    if not CampaignMembership.objects.filter(
        campaign=campaign_obj, user_id=body.owner_id, status=2
    ).exists():
        return Response({"error": "Only the owner can add members"}, status=403)

    try:
        user = Player.objects.get(id=body.user_id)
    except Player.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    membership, created = CampaignMembership.objects.get_or_create(
        user=user, campaign=campaign_obj, defaults={"status": 0}
    )
    if not created:
        membership.status = 0
        membership.save()

    return Response(
        {"message": f"User {user.id} added to campaign {campaign_obj.id}"},
        status=201 if created else 200,
    )


class CampaignEditPermissions(Schema):
    campaign_id: int
    owner_id: int
    user_id: int
    status: int

@router.post("edit-permissions/")
def edit_permissions_view(request, body: CampaignEditPermissions) -> Response:
    if body.status not in [0, 1, 2]:
        return Response({"error": "Invalid status value"}, status=400)

    try:
        campaign_obj = Campaign.objects.get(id=body.campaign_id)
    except Campaign.DoesNotExist:
        return Response({"error": "Campaign not found"}, status=404)

    # Verify owner permissions
    if not CampaignMembership.objects.filter(
        campaign=campaign_obj, user_id=body.owner_id, status=2
    ).exists():
        return Response({"error": "Only the owner can edit permissions"}, status=403)

    try:
        membership = CampaignMembership.objects.get(campaign=campaign_obj, user_id=body.user_id)
    except CampaignMembership.DoesNotExist:
        return Response({"error": "Membership not found"}, status=404)

    membership.status = body.status
    membership.save()

    return Response(
        {"message": f"Updated user {body.user_id} role to {body.status} in campaign {campaign_obj.id}"},
        status=200,
    )
