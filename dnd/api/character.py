from django.http import HttpRequest
from ninja import Router
from ninja.responses import Response

from dnd.models import Campaign, Character, Player
from dnd.schemas.character import CharacterOut, UploadCharacter

router = Router()


@router.get("/get/")
def get_character_api(request: HttpRequest, char_id: int) -> Response:
    char_obj = Character.objects.filter(id=char_id)
    if not char_obj.exists():
        return Response({}, status=404)
    char_obj = char_obj.first()

    return CharacterOut(
        id=char_obj.id,
        owner_id=char_obj.owner_id,
        owner_telegram_id=char_obj.owner.telegram_id,
        data=char_obj.load_data(),
        campaign_id=char_obj.campaign_id,
    )


@router.post("post/", response={201: CharacterOut})
def upload_character_api(request: HttpRequest, upload: UploadCharacter):
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

    return 201, CharacterOut(
        id=char_obj.id,
        owner_id=char_obj.owner_id,
        owner_telegram_id=char_obj.owner.telegram_id,
        data=char_obj.load_data(),
        campaign_id=char_obj.campaign_id,
    )
