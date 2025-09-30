from drf_yasg import openapi

character_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'char_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the character'),
        'owner_telegram_id': openapi.Schema(type=openapi.TYPE_STRING, description='Telegram ID of the character owner'),
        'char_data': openapi.Schema(type=openapi.TYPE_OBJECT, description='Character data', additional_properties=True),
        'campaign_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the campaign'),
    },
    required=['char_id', 'owner_telegram_id', 'char_data', 'campaign_id']
)

upload_character_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'owner_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the player owning the character'),
        'campaign_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the campaign'),
        'data': openapi.Schema(type=openapi.TYPE_OBJECT, description='Character data', additional_properties=True),
    },
    required=['owner_id', 'campaign_id', 'data']
)

upload_character_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'char_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the created character'),
        'char_owner_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the character owner'),
        'campaign_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the campaign'),
    },
    required=['char_id', 'char_owner_id', 'campaign_id']
)