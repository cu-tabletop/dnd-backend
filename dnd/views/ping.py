from ninja import Router
from ninja.responses import Response

router = Router()

@router.get("/", url_name="ping")
def ping(request):
    return Response({
        'message': 'hello',
    }, status=200)
