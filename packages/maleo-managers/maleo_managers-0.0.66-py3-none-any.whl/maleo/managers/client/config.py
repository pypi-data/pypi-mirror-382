from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar
from .maleo.config import MaleoClientsConfigT


class ClientConfig(BaseModel, Generic[MaleoClientsConfigT]):
    maleo: MaleoClientsConfigT = Field(
        ...,
        description="Maleo client's configurations",
    )


ClientConfigT = TypeVar("ClientConfigT", bound=Optional[ClientConfig])


class ClientConfigMixin(BaseModel, Generic[ClientConfigT]):
    client: ClientConfigT = Field(..., description="Client config")
