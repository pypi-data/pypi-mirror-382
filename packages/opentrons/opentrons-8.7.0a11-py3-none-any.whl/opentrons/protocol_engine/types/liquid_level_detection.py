"""Protocol Engine types to do with liquid level detection."""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, model_serializer, model_validator


class SimulatedProbeResult(BaseModel):
    """A sentinel value to substitute for the resulting volume/height of a liquid probe during simulation."""

    operations_after_probe: List[float] = []
    net_liquid_exchanged_after_probe: float = 0.0

    @model_serializer
    def serialize_model(self) -> str:
        """Serialize instances of this class as a string."""
        return "SimulatedProbeResult"

    @model_validator(mode="before")
    @classmethod
    def validate_model(cls, data: object) -> Any:
        """Handle deserializing from a simulated probe result."""
        if isinstance(data, str) and data == "SimulatedProbeResult":
            return {}
        return data

    def __add__(
        self, other: float | int | SimulatedProbeResult
    ) -> float | SimulatedProbeResult:
        """Bypass addition and just return self."""
        return self

    def __sub__(
        self, other: float | int | SimulatedProbeResult
    ) -> float | SimulatedProbeResult:
        """Bypass subtraction and just return self."""
        return self

    def __radd__(
        self, other: float | int | SimulatedProbeResult
    ) -> float | SimulatedProbeResult:
        """Bypass addition and just return self."""
        return self

    def __rsub__(
        self, other: float | int | SimulatedProbeResult
    ) -> float | SimulatedProbeResult:
        """Bypass subtraction and just return self."""
        return self

    def __mul__(
        self, other: float | int | SimulatedProbeResult
    ) -> float | SimulatedProbeResult:
        """Bypass multiplication and just return self."""
        return self

    def __rmul__(
        self, other: float | int | SimulatedProbeResult
    ) -> float | SimulatedProbeResult:
        """Bypass multiplication and just return self."""
        return self

    def __truediv__(
        self, other: float | int | SimulatedProbeResult
    ) -> float | SimulatedProbeResult:
        """Bypass division and just return self."""
        return self

    def __rtruediv__(
        self, other: float | int | SimulatedProbeResult
    ) -> float | SimulatedProbeResult:
        """Bypass division and just return self."""
        return self

    def __pow__(
        self, other: float | int | SimulatedProbeResult
    ) -> float | SimulatedProbeResult:
        """Bypass exponent math and just return self."""
        return self

    def __rpow__(
        self, other: float | int | SimulatedProbeResult
    ) -> float | SimulatedProbeResult:
        """Bypass exponent math and just return self."""
        return self

    def __mod__(
        self, other: float | int | SimulatedProbeResult
    ) -> float | SimulatedProbeResult:
        """Bypass modulus and just return self."""
        return self

    def __rmod__(
        self, other: float | int | SimulatedProbeResult
    ) -> float | SimulatedProbeResult:
        """Bypass modulus and just return self."""
        return self

    def __floordiv__(
        self, other: float | int | SimulatedProbeResult
    ) -> float | SimulatedProbeResult:
        """Bypass floor division and just return self."""
        return self

    def __rfloordiv__(
        self, other: float | int | SimulatedProbeResult
    ) -> float | SimulatedProbeResult:
        """Bypass floor division and just return self."""
        return self

    def __gt__(self, other: float | int | SimulatedProbeResult) -> bool:
        """Bypass 'greater than' and just return self."""
        return True

    def __lt__(self, other: float | int | SimulatedProbeResult) -> bool:
        """Bypass 'less than' and just return self."""
        return False

    def __ge__(self, other: float | int | SimulatedProbeResult) -> bool:
        """Bypass 'greater than or eaqual to' and just return self."""
        return True

    def __le__(self, other: float | int | SimulatedProbeResult) -> bool:
        """Bypass 'less than or equal to' and just return self."""
        return False

    def __eq__(self, other: object) -> bool:
        """A SimulatedProbeResult should only be equal to the same instance of its class."""
        if not isinstance(other, SimulatedProbeResult):
            return False
        return self is other

    def __neq__(self, other: object) -> bool:
        """A SimulatedProbeResult should only be equal to the same instance of its class."""
        if not isinstance(other, SimulatedProbeResult):
            return True
        return self is not other

    def simulate_probed_aspirate_dispense(self, volume: float) -> None:
        """Record the current state of aspirate/dispense calls."""
        self.net_liquid_exchanged_after_probe += volume
        self.operations_after_probe.append(volume)


# Work around https://github.com/pydantic/pydantic/issues/6830 - do not change the order of
# this union
LiquidTrackingType = float | SimulatedProbeResult


class LoadedVolumeInfo(BaseModel):
    """A well's liquid volume, initialized by a LoadLiquid, updated by Aspirate and Dispense."""

    volume: LiquidTrackingType | None = None
    last_loaded: datetime
    operations_since_load: int


class ProbedHeightInfo(BaseModel):
    """A well's liquid height, initialized by a LiquidProbe, cleared by Aspirate and Dispense."""

    height: LiquidTrackingType | None = None
    last_probed: datetime


class ProbedVolumeInfo(BaseModel):
    """A well's liquid volume, initialized by a LiquidProbe, updated by Aspirate and Dispense."""

    volume: LiquidTrackingType | None = None
    last_probed: datetime
    operations_since_probe: int


class WellInfoSummary(BaseModel):
    """Payload for a well's liquid info in StateSummary."""

    labware_id: str
    well_name: str
    loaded_volume: Optional[float] = None
    probed_height: LiquidTrackingType | None = None
    probed_volume: LiquidTrackingType | None = None


@dataclass
class WellLiquidInfo:
    """Tracked and sensed information about liquid in a well."""

    probed_height: Optional[ProbedHeightInfo]
    loaded_volume: Optional[LoadedVolumeInfo]
    probed_volume: Optional[ProbedVolumeInfo]
