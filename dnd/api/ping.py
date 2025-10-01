from ninja import Router

from dnd.schemas import Message

router = Router()


@router.get("/", url_name="ping", response={200: Message})
def ping(request):
    return Message(message="hello")
