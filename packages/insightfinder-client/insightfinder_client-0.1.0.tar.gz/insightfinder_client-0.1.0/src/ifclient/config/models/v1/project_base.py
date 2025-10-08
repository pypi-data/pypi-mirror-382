from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, Union, List
from ifclient.config.models.common.file_reference import FileReference
from ifclient.config.models.v1.instance_grouping import InstanceGrouping, InstanceGroupingSettingV1
from ifclient.config.models.v1.component_metric import MetricSetting, ComponentMetricSettingV1

class ProjectBaseV1(BaseModel):

    model_config = ConfigDict(
        validate_assignment=True
    )

    apiVersion: Literal["v1"] = Field(
        ...,
        description="API Version",
        exclude=True
    )
    type: Literal["projectBase"] = Field(
        ...,
        description="Type of configuration",
        exclude=True
    )

    project: str = Field(
        ...,
        description="Project name on InsightFinder to apply the following settings to"
    )

    userName: str = Field(
        ...,
        description="username of the user owning the project"
    )

    # Common settings for both log and metric projects
    cValue: Optional[int] = Field(
        default=None,
        description="Continues value for project, unit is count",
        examples=[1]
    )
    pValue: Optional[float] = Field(
        default=None,
        description="The probability threshold value for UBL.",
        examples=[0.95]
    )
    showInstanceDown: Optional[bool] = Field(
        default=None,
        description="Whether to show instance down incidents for this project.",
        examples=[False]
    )
    retentionTime: Optional[int] = Field(
        default=None,
        description="The retention time in days.",
        examples=[15]
    )
    UBLRetentionTime: Optional[int] = Field(
        default=None,
        description="Retention time for UBL data in days.",
        examples=[30]
    )
    projectDisplayName: Optional[str] = Field(
        default=None,
        description="The display name of the project.",
        examples=["Project-1"]
    )
    samplingInterval: Optional[int] = Field(
        default=None,
        description="The interval for sampling in seconds. Don't change this unless necessary",
        examples=[60]
    )

    instanceGroupingUpdate: Union[None, FileReference, InstanceGrouping, List[InstanceGroupingSettingV1]] = Field(
        default=None,
        description="File paths to instanceGroupingData configurations",
        examples=[
            "/abs/path/to/config/files/group1.yaml",
            "./relative/path/to/config/files/group2.yaml",
            "./relative/path/with/wilcards/*.yaml"
        ]
    )
    componentMetricSettingOverallModelList: Union[None, FileReference, List[MetricSetting], List[ComponentMetricSettingV1]] = Field(
        default=None,
        description="File paths to componentMetricSettingOverallModelList configurations",
        examples=[
            "/abs/path/to/config/files/group1.yaml",
            "./relative/path/to/config/files/group2.yaml",
            "./relative/path/with/wilcards/*.yaml"
        ]
    )

    # Following settings applicable for only metric projects
    highRatioCValue: Optional[int] = Field(
        default=None,
        description="c value for those anomaly with 1000% higher than normal, needs to be smaller than normal c value",
        examples=[1]
    )
    dynamicBaselineDetectionFlag: Optional[bool] = Field(
        default=None,
        description="Enable Baseline Detection",
        examples=[True]
    )
    positiveBaselineViolationFactor: Optional[float] = Field(
        default=None,
        description="The baseline violation factor for higher than normal detection",
        examples=[2.0]
    )
    negativeBaselineViolationFactor: Optional[float] = Field(
        default=None,
        description="The baseline violation factor for lower than normal detection",
        examples=[2.0]
    )
    enablePeriodAnomalyFilter: Optional[bool] = Field(
        default=None,
        description="Enable period detection, usually false this is very resource consuming",
        examples=[False]
    )
    enableUBLDetect: Optional[bool] = Field(
        default=None,
        description="Enable UBL Detection",
        examples=[True]
    )
    enableCumulativeDetect: Optional[bool] = Field(
        default=None,
        description="Enable Auto-Cumulative Detection",
        examples=[True]
    )
    instanceDownThreshold: Optional[int] = Field(
        default=None,
        description="How long instance down will generate incident, unit is milliseconds",
        examples=[3600000]
    )
    instanceDownReportNumber: Optional[int] = Field(
        default=None,
        description="How many instance down instances will be reported",
        examples=[5]
    )
    instanceDownEnable: Optional[bool] = Field(
        default=None,
        description="Enable instance down report",
        examples=[True]
    )
    modelSpan: Optional[int] = Field(
        default=None,
        description="Model span setting. 0 is daily, 1 is monthly",
        examples=[0]
    )
    enableMetricDataPrediction: Optional[bool] = Field(
        default=None,
        description="Enable metric data prediction",
        examples=[True]
    )
    enableBaselineDetectionDoubleVerify: Optional[bool] = Field(
        default=None,
        description="Enable metric baseline double verification, normally disabled",
        examples=[False]
    )
    enableFillGap: Optional[bool] = Field(
        default=None,
        description="Enable metric data gap filling for missing data, normally disabled",
        examples=[False]
    )
    patternIdGenerationRule: Optional[int] = Field(
        default=None,
        description="0 or 1. Generate pattern name and id by metric type (0) or metric name (1)",
        examples=[0]
    )
    anomalyGapToleranceCount: Optional[int] = Field(
        default=None,
        description="Gap tolerance value, 0 means disabled",
        examples=[0]
    )
    filterByAnomalyInBaselineGeneration: Optional[bool] = Field(
        default=None,
        description="Filter out anomaly part when generating baseline, normally false",
        examples=[False]
    )
    baselineDuration: Optional[int] = Field(
        default=None,
        description="Baseline block duration, unit is milliseconds",
        examples=[21600000]
    )


    
    


