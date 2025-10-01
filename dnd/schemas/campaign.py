from ninja import ModelSchema, Schema

from ..models import Campaign


class CreateCampaignRequest(Schema):
    telegram_id: int
    title: str
    icon: str | None = None
    description: str | None = None


class CampaignModelSchema(ModelSchema):
    class Meta:
        model = Campaign
        fields = ['id', 'title', 'description', 'icon', 'verified', 'private']
        fields_optional = ['icon', 'description']
