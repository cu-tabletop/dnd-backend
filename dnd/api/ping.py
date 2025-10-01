from ninja import Router

from dnd.schemas import PingResponse

router = Router()


@router.get("/", url_name="ping", response=PingResponse)
def ping(request):
    return PingResponse(message="hello")
