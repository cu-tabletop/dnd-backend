from ninja import ModelSchema

from ..models import Campaign


class CampaignOut(ModelSchema):
    class Meta:
        model = Campaign
        fields = ['id', 'title', 'description', 'icon', 'verified', 'private']
        fields_optional = ['icon', 'description']
