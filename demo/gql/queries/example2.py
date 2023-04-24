"""
Generated by qenerate plugin=pydantic_v1. DO NOT MODIFY MANUALLY!
"""
from collections.abc import Callable  # noqa: F401 # pylint: disable=W0611
from datetime import datetime  # noqa: F401 # pylint: disable=W0611
from enum import Enum  # noqa: F401 # pylint: disable=W0611
from typing import (  # noqa: F401 # pylint: disable=W0611
    Any,
    Optional,
    Union,
)

from pydantic import (  # noqa: F401 # pylint: disable=W0611
    BaseModel,
    Extra,
    Field,
    Json,
)

from demo.gql.fragments.fragment1 import VaultSecret


DEFINITION = """
fragment VaultSecret on VaultSecret_v1 {
    path
    field
    version
    format
}

query GitlabInstance {
  instances: gitlabinstance_v1 {
    url
    token {
      # Here we use the fragment defined in fragment1.gql
      ... VaultSecret
    }
  }
}
"""


class ConfiguredBaseModel(BaseModel):
    class Config:
        smart_union=True
        extra=Extra.forbid


class GitlabInstanceV1(ConfiguredBaseModel):
    url: str = Field(..., alias="url")
    token: VaultSecret = Field(..., alias="token")


class GitlabInstanceQueryData(ConfiguredBaseModel):
    instances: Optional[list[GitlabInstanceV1]] = Field(alias="instances")


def query(query_func: Callable, **kwargs: Any) -> GitlabInstanceQueryData:
    """
    This is a convenience function which queries and parses the data into
    concrete types. It should be compatible with most GQL clients.
    You do not have to use it to consume the generated data classes.
    Alternatively, you can also mime and alternate the behavior
    of this function in the caller.

    Parameters:
        query_func (Callable): Function which queries your GQL Server
        kwargs: optional arguments that will be passed to the query function

    Returns:
        GitlabInstanceQueryData: queried data parsed into generated classes
    """
    raw_data: dict[Any, Any] = query_func(DEFINITION, **kwargs)
    return GitlabInstanceQueryData(**raw_data)
