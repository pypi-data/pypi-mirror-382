from pydantic import BaseModel, Field
from typing import Annotated
from .resource.config import ConfigMixin as ResourceConfigMixin


class Config(ResourceConfigMixin):
    pass


class ConfigMixin(BaseModel):
    infra: Annotated[
        Config, Field(default_factory=Config, description="Infra config")
    ] = Config()
