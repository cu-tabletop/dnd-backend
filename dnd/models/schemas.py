from ninja import Schema


class CampaignOut(Schema):
    id: int
    title: str
    description: str
    icon: str | None = None
    verified: bool
    private: bool
