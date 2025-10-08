from pydantic import BaseModel, Field
from typing import Annotated


class MeasurementConfig(BaseModel):
    interval: Annotated[
        float, Field(300.0, description="Monitor interval (s)", ge=1.0)
    ] = 300.0
    frequency: Annotated[int, Field(1, description="Logging frequency", ge=1)] = 1
    window: Annotated[int, Field(5, description="Smoothing window", ge=5)] = 5


class ThresholdConfig(BaseModel):
    low: Annotated[float, Field(10.0, description="Low", ge=0.0)] = 10.0
    normal: Annotated[float, Field(75.0, description="Normal", ge=0.0)] = 75.0
    high: Annotated[float, Field(85.0, description="High", ge=0.0)] = 85.0
    critical: Annotated[float, Field(95.0, description="Critical", ge=0.0)] = 95.0


class CPUUsageConfig(BaseModel):
    threshold: Annotated[
        ThresholdConfig, Field(default_factory=ThresholdConfig, description="Threshold")
    ] = ThresholdConfig()


class MemoryUsageConfig(BaseModel):
    limit: Annotated[
        float,
        Field(
            256.0, description="Memory limit (MB) applied to raw memory value", ge=0.0
        ),
    ] = 256.0
    threshold: Annotated[
        ThresholdConfig, Field(default_factory=ThresholdConfig, description="Threshold")
    ] = ThresholdConfig()


class UsageConfig(BaseModel):
    cpu: Annotated[
        CPUUsageConfig, Field(default_factory=CPUUsageConfig, description="CPU Usage")
    ] = CPUUsageConfig()
    memory: Annotated[
        MemoryUsageConfig,
        Field(default_factory=MemoryUsageConfig, description="Memory Usage"),
    ] = MemoryUsageConfig()


class Config(BaseModel):
    measurement: Annotated[
        MeasurementConfig,
        Field(
            default_factory=MeasurementConfig,
            description="Resource usage configuration",
        ),
    ] = MeasurementConfig()

    retention: Annotated[
        int,
        Field(
            3600,
            description="Monitor data retention (s)",
            ge=60,
            le=7200,
            multiple_of=60,
        ),
    ] = 3600

    usage: Annotated[
        UsageConfig, Field(default_factory=UsageConfig, description="Usage config")
    ] = UsageConfig()


class ConfigMixin(BaseModel):
    resource: Annotated[
        Config, Field(default_factory=Config, description="Resource config")
    ] = Config()
