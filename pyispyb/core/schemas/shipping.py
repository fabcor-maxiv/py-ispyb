from datetime import datetime
import enum
from typing import Optional
from pydantic import BaseModel, Field

from ispyb import models

d = models.Dewar


class SafetyLevelEnum(str, enum.Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class ShippingCreate(BaseModel):
    proposalId: int
    shippingName: str = Field(title="Name")
    sendingLabContactId: int = Field(title="Sending Lab Contact")
    returnLabContactId: int = Field(title="Return Lab Contact")
    shippingStatus: str = Field(title="Shipping Status")
    safetyLevel: SafetyLevelEnum = Field(title="Safety Level", default="GREEN")
    comments: Optional[str] = Field(title="Comments")


class ShippingMetaData(BaseModel):
    dewars: int = Field(description="Number of dewars")
    samples: Optional[int] = Field(description="Number of samples")
    sessions: list['pyispyb.core.schemas.sessions.SessionReadBase'] | None = Field(description="Sessions")


class ShippingLabContactPerson(BaseModel):
    givenName: str
    familyName: str

    class Config:
        orm_mode = True


class ShippingLabContact(BaseModel):
    cardName: str

    Person: ShippingLabContactPerson

    class Config:
        orm_mode = True


class ShippingBase(ShippingCreate):

    shippingId: int
    bltimeStamp: Optional[datetime] = Field(title="Created at")

    sendingLabContactId: Optional[int] = Field(title="Sending Lab Contact")
    returnLabContactId: Optional[int] = Field(title="Return Lab Contact")
    safetyLevel: Optional[SafetyLevelEnum] = Field(title="Safety Level")
    shippingStatus: Optional[str] = Field(title="Shipping Status")

    LabContact: Optional[ShippingLabContact] = Field(title="Return Lab Contact")
    LabContact1: Optional[ShippingLabContact] = Field(title="Sending Lab Contact")

    class Config:
        orm_mode = True
        json_encoders = {datetime: lambda obj: obj.isoformat() + "+00:00"}


class Shipping(ShippingBase):
    metadata: Optional[ShippingMetaData] = Field(alias="_metadata")


class Dewar(BaseModel):
    code: str = Field(title="Name")

    Shipping: Shipping

    class Config:
        orm_mode = True


class Container(BaseModel):
    code: str = Field(title="Name")

    sampleChangerLocation: Optional[str] = Field(
        description="Position in sample change"
    )
    beamlineLocation: Optional[str] = Field(
        description="Beamline if container is assigned"
    )

    Dewar: Dewar

    class Config:
        orm_mode = True
