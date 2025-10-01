from ninja import Router, Schema
from ninja.responses import Response

from ..models import *

router = Router()

@router.get('/get/')
def get_character_api(request, char_id: int) -> Response:
    char_obj = Character.objects.filter(id=char_id)
    if not char_obj.exists():
        return Response({}, status=404)
    char_obj = char_obj.first()

    return Response(data={
        'char_id': char_obj.id,
        'owner_telegram_id': char_obj.owner.telegram_id,
        'char_data': char_obj.load_data(),
        'campaign_id': char_obj.campaign_id,
    }, status=200)

class UploadCharacter(Schema):
    owner_id: int
    campaign_id: int
    data: dict

@router.post("post/")
def upload_character_api(request, upload: UploadCharacter):
    owner_obj = Player.objects.filter(id=upload.owner_id)
    if not owner_obj.exists():
        return Response({}, status=404)
    owner_obj = owner_obj.first()

    campaign_obj = Campaign.objects.filter(id=upload.campaign_id)
    if not campaign_obj.exists():
        return Response({}, status=404)
    campaign_obj = campaign_obj.first()

    char_obj = Character.objects.create(owner=owner_obj, campaign=campaign_obj)
    char_obj.save_data(upload.data)

    return Response({
        "char_id": char_obj.id,
        "char_owner_id": char_obj.owner_id,
        "campaign_id": char_obj.campaign_id,
    }, status=201)
