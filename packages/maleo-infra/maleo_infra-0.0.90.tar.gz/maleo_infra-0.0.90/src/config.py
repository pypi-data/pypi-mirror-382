from pydantic import BaseModel, Field
from typing import Annotated
from .resource.config import ResourceConfigMixin


class InfraConfig(ResourceConfigMixin):
    pass


class InfraConfigMixin(BaseModel):
    infra: Annotated[
        InfraConfig, Field(default_factory=InfraConfig, description="Infra config")
    ] = InfraConfig()
