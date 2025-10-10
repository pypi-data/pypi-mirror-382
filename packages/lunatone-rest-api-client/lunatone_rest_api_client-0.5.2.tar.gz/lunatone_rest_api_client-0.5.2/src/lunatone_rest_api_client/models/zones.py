from pydantic import BaseModel, Field, PositiveInt, NonNegativeInt

from lunatone_rest_api_client.models import FeaturesStatus, TimeSignature


class ZoneTarget(BaseModel):
    type: str
    id: NonNegativeInt | None = None


class ZoneData(BaseModel):
    id: PositiveInt
    name: str = ""
    targets: list[ZoneTarget] = []
    features: FeaturesStatus = FeaturesStatus()
    time_signature: TimeSignature | None = Field(None, alias="timeSignature")


class ZonesData(BaseModel):
    zones: list[ZoneData]
    time_signature: TimeSignature | None = Field(None, alias="timeSignature")
