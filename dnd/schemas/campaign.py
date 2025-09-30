from drf_yasg import openapi

create_campaign_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "telegram_id": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="Telegram ID of the user creating the campaign",
        ),
        "title": openapi.Schema(
            type=openapi.TYPE_STRING, description="Title of the campaign"
        ),
        "icon": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Base64-encoded PNG image for the campaign icon",
            nullable=True,
        ),
        "description": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="Description of the campaign",
            nullable=True,
        ),
    },
    required=["telegram_id", "title"],
)

create_campaign_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "message": openapi.Schema(
            type=openapi.TYPE_STRING, description="Success message"
        ),
        "campaign_id": openapi.Schema(
            type=openapi.TYPE_INTEGER, description="ID of the created campaign"
        ),
    },
)

campaign_info_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Campaign ID"),
        "title": openapi.Schema(type=openapi.TYPE_STRING, description="Campaign title"),
        "description": openapi.Schema(
            type=openapi.TYPE_STRING, description="Campaign description", nullable=True
        ),
        "icon": openapi.Schema(
            type=openapi.TYPE_STRING,
            description="URL or base64 of the campaign icon",
            nullable=True,
        ),
        "private": openapi.Schema(
            type=openapi.TYPE_BOOLEAN, description="Whether the campaign is private"
        ),
        "verified": openapi.Schema(
            type=openapi.TYPE_BOOLEAN, description="Whether the campaign is verified"
        ),
    },
)

campaigns_list_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "campaigns": openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=campaign_info_response_schema,
            description="List of campaigns",
        )
    },
)

add_to_campaign_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "campaign_id": openapi.Schema(
            type=openapi.TYPE_INTEGER, description="ID of the campaign"
        ),
        "owner_id": openapi.Schema(
            type=openapi.TYPE_INTEGER, description="ID of the campaign owner"
        ),
        "user_id": openapi.Schema(
            type=openapi.TYPE_INTEGER, description="ID of the user to add"
        ),
    },
    required=["campaign_id", "owner_id", "user_id"],
)

add_to_campaign_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "message": openapi.Schema(
            type=openapi.TYPE_STRING, description="Success message"
        )
    },
)

edit_permissions_request_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "campaign_id": openapi.Schema(
            type=openapi.TYPE_INTEGER, description="ID of the campaign"
        ),
        "owner_id": openapi.Schema(
            type=openapi.TYPE_INTEGER, description="ID of the campaign owner"
        ),
        "user_id": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="ID of the user whose permissions are being edited",
        ),
        "status": openapi.Schema(
            type=openapi.TYPE_INTEGER,
            description="New status (0: player, 1: master, 2: owner)",
            enum=[0, 1, 2],
        ),
    },
    required=["campaign_id", "owner_id", "user_id", "status"],
)

edit_permissions_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "message": openapi.Schema(
            type=openapi.TYPE_STRING, description="Success message"
        )
    },
)

error_response_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "error": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
    },
)
