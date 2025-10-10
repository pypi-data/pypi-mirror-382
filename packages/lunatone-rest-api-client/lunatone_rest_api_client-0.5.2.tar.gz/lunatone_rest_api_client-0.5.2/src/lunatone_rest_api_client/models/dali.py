from enum import StrEnum

from pydantic import BaseModel, Field, NonNegativeInt


class StartScanData(BaseModel):
    new_installation: bool = Field(False, alias="newInstallation")
    no_addressing: bool = Field(False, alias="noAddressing")
    use_lines: list[NonNegativeInt] = Field([], alias="useLines")


class ScanState(StrEnum):
    NOT_STARTED = "not started"
    CANCELLED = "cancelled"
    DONE = "done"
    ADDRESSING = "addressing"
    IN_PROGRESS = "in progress"


class ScanData(BaseModel):
    id: str = ""
    progress: float | None = None
    found: int | None = None
    found_sensors: int | None = Field(None, alias="foundSensors")
    status: ScanState = ScanState.NOT_STARTED
    lines: list[dict] = []
