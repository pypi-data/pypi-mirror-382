from datetime import datetime
from pydantic import BaseModel, Field
from typing import Annotated, Generic, TypeVar
from .config import CPUUsageConfig, MemoryUsageConfig
from .enums import Status


class CPUUsage(BaseModel):
    raw: Annotated[float, Field(..., description="Raw CPU Usage (%)", ge=0.0, le=100.0)]
    smooth: Annotated[
        float, Field(..., description="Smooth CPU Usage (%)", ge=0.0, le=100.0)
    ]
    status: Annotated[Status, Field(Status.NORMAL, description="Usage status")] = (
        Status.NORMAL
    )

    @classmethod
    def new(
        cls,
        *,
        raw: float,
        smooth: float,
        config: CPUUsageConfig,
    ) -> "CPUUsage":
        if smooth < config.threshold.low:
            status = Status.LOW
        elif smooth < config.threshold.normal:
            status = Status.NORMAL
        elif smooth < config.threshold.high:
            status = Status.HIGH
        elif smooth < config.threshold.critical:
            status = Status.CRITICAL
        else:
            status = Status.OVERLOAD

        return cls(raw=raw, smooth=smooth, status=status)


class MemoryUsage(BaseModel):
    raw: Annotated[float, Field(..., description="Raw memory usage (MB)", ge=0.0)]
    percentage: Annotated[float, Field(..., description="Percentage of limit", ge=0.0)]
    status: Annotated[Status, Field(Status.NORMAL, description="Usage status")] = (
        Status.NORMAL
    )

    @classmethod
    def new(cls, raw: float, config: MemoryUsageConfig) -> "MemoryUsage":
        percentage = (raw / config.limit) * 100
        if percentage < config.threshold.low:
            status = Status.LOW
        elif percentage < config.threshold.normal:
            status = Status.NORMAL
        elif percentage < config.threshold.high:
            status = Status.HIGH
        elif percentage < config.threshold.critical:
            status = Status.CRITICAL
        else:
            status = Status.OVERLOAD

        return cls(raw=raw, percentage=percentage, status=status)


class Usage(BaseModel):
    cpu: Annotated[CPUUsage, Field(..., description="CPU Usage")]
    memory: Annotated[MemoryUsage, Field(..., description="Memory Usage")]


UsageT = TypeVar("UsageT", bound=Usage)


class AggregateUsage(Usage):
    window: Annotated[int, Field(..., description="Measurement window")]


class Measurement(BaseModel, Generic[UsageT]):
    measured_at: Annotated[datetime, Field(..., description="Measured at timestamp")]
    status: Annotated[Status, Field(..., description="Aggregate status")]
    usage: Annotated[UsageT, Field(..., description="Resource usage")]
