from ninja import NinjaAPI

api = NinjaAPI()

api.add_router("/", "dnd.urls.dnd_api")
