from ninja import Schema


class UploadCharacter(Schema):
    owner_id: int
    campaign_id: int
    data: dict
