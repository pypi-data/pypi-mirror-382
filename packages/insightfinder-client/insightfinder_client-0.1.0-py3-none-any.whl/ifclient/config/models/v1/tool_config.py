from pydantic import BaseModel, AnyUrl, Field
from typing import Literal, Union, List
from ifclient.config.models.common.file_reference import FileReference
from ifclient.config.models.v1.project_base import ProjectBaseV1

class ToolConfigV1(BaseModel):
    apiVersion: Literal["v1"] = Field(
        ...,
        description="API Version",
        exclude=True
    )
    type: Literal["toolConfig"] = Field(
        ...,
        description="Type of configuration",
        exclude=True
    )

    baseUrl: AnyUrl = Field(
        description="InsightFinder URL where projects are hosted"
    )

    projectBaseConfigs: Union[None, FileReference, List[ProjectBaseV1]] = Field(
        ...,
        description="List of paths to project base configurations"
    )
