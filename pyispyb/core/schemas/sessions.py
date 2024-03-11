# import datetime
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SessionMetaData(BaseModel):
    samples: Optional[int] = Field(description="Number of samples")
    datacollections: Optional[int] = Field(description="Number of datacollections")
    energy_scans: Optional[int] = Field(description="Number of energy scans")
    xrf_scans: Optional[int] = Field(description="Number of XRF scans")
    uiGroups: Optional[list[str]] = Field(description="UI groups for this session")
    persons: Optional[int] = Field(
        description="Number of people registered on this session (via SessionHasPerson)"
    )
    active: Optional[bool] = Field(description="Whether this session is active")
    active_soon: Optional[bool] = Field(
        description="Whether this session is due to start soon or has ended recently (+/-20 min)"
    )
    sessionTypes: Optional[list[str]] = Field(
        description="Session types for this session"
    )


class BeamLineSetupWrite(BaseModel):
    """Used for CREATE and UPDATE operations (CRUD)."""

    synchrotronMode: Optional[str]
    undulatorType1: Optional[str]
    undulatorType2: Optional[str]
    undulatorType3: Optional[str]
    focalSpotSizeAtSample: Optional[float]
    focusingOptic: Optional[str]
    beamDivergenceHorizontal: Optional[float]
    beamDivergenceVertical: Optional[float]
    polarisation: Optional[float]
    monochromatorType: Optional[str]
    setupDate: Optional[datetime]
    synchrotronName: Optional[str]
    maxExpTimePerDataCollection: Optional[float]
    minExposureTimePerImage: Optional[float]
    goniostatMaxOscillationSpeed: Optional[float]
    goniostatMinOscillationWidth: Optional[float]
    minTransmission: Optional[float]
    CS: Optional[float]


class BeamLineSetupRead(BeamLineSetupWrite):
    """Used for READ operations (CRUD)."""

    beamLineSetupId: int

    class Config:
        orm_mode = True


class SessionCreate(BaseModel):
    """Used for CREATE operations (CRUD)."""

    proposalId: int

    startDate: datetime
    endDate: datetime

    nbShifts: int
    scheduled: bool

    beamLineName: str
    BeamLineSetup: BeamLineSetupWrite | None

    comments: str


class SessionUpdate(BaseModel):
    """Used for UPDATE operations (CRUD)."""

    BeamLineSetup: BeamLineSetupWrite


class SessionReadBase(BaseModel):
    """Used for READ operations (CRUD), without metadata."""

    sessionId: int
    session: str

    proposalId: int
    proposal: str

    startDate: datetime
    endDate: datetime

    lastUpdate: datetime | None

    nbShifts: int | None
    scheduled: bool
    visit_number: int | None

    beamLineName: str
    beamLineOperator: str | None
    BeamLineSetup: BeamLineSetupRead | None

    comments: str | None

    nbReimbDewars: int | None


class SessionRead(SessionReadBase):
    """Used for READ operations (CRUD), with metadata."""

    metadata: SessionMetaData = Field(alias="_metadata")

    class Config:
        orm_mode = True
