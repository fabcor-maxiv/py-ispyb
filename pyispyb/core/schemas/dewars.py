import enum
from typing import Optional
from pydantic import BaseModel, Field

from ispyb import models

d = models.Dewar


class DewarShipping(BaseModel):
    proposalId: int
    shippingName: str = Field(title="Name")

    class Config:
        orm_mode = True


class DewarCreate(BaseModel):
    shippingId: int
    code: str = Field(title="Name")
    dewarType: Optional[str]


class DewarType(str, enum.Enum):
    Dewar = "Dewar"
    Toolbox = "Toolbox"


class DewarMetaData(BaseModel):
    containers: Optional[int] = Field(description="Number of containers")


class Dewar(DewarCreate):
    dewarId: int
    code: str
    comments: Optional[str]
    storageLocation: Optional[str]
    dewarStatus: Optional[str]
    # bltimeStamp
    isStorageDewar: Optional[bool]
    barCode: Optional[str]
    customsValue: Optional[int]
    transportValue: Optional[int]
    trackingNumberToSynchrotron: Optional[str]
    trackingNumberFromSynchrotron: Optional[str]
    facilityCode: Optional[str]
    type: Optional[DewarType]
    isReimbursed: Optional[bool]

    Shipping: DewarShipping
    metadata: DewarMetaData = Field(alias="_metadata")

    class Config:
        orm_mode = True
