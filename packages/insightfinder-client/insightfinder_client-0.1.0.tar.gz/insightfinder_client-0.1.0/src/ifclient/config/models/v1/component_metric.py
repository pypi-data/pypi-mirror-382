from pydantic import BaseModel, Field 
from typing import Optional, List, Literal


class MetricSetting(BaseModel):
    # Required fields
    metricName: str = Field(
        ...,
        description="Metric Name",
        examples=["metric1"]
    )
    thresholdAlertLowerBound: float = Field(
        ...,
        description="Float value or empty",
        examples=[]
    )
    thresholdAlertUpperBound: float = Field(
        ...,
        description="Float value or empty",
        examples=[]
    )
    thresholdAlertUpperBoundNegative: float = Field(
        ...,
        description="Float value or empty",
        examples=[]
    )
    thresholdAlertLowerBoundNegative: float = Field(
        ...,
        description="Float value or empty",
        examples=[]
    )
    thresholdNoAlertLowerBound: float = Field(
        ...,
        description="Float value or empty",
        examples=[]
    )
    thresholdNoAlertUpperBound: float = Field(
        ...,
        description="Float value or empty",
        examples=[]
    )
    thresholdNoAlertLowerBoundNegative: float = Field(
        ...,
        description="Float value or empty",
        examples=[]
    )
    thresholdNoAlertUpperBoundNegative: float = Field(
        ...,
        description="Float value or empty",
        examples=[]
    )
    
    # Optional fields
    isKPI: Optional[bool] = Field(
        default=None,
        description="Set metric as KPI",
        examples=[False]
    )
    escalateIncidentSet: Optional[List[str]] = Field(
        default=None,
        description="Set of components' anomalies to be escalated to incident. Another setting for all components below",
        examples=[["component1, component2, component5"]]
    )
    escalateIncidentAll: Optional[bool] = Field(
        default=None,
        description="Escalate all components' anomalies to incidents",
        examples=[False]
    )
    patternNameHigher: Optional[str] = Field(
        default=None,
        description="Higher than normal pattern name",
        examples=["pattern-higer"]
    )
    patternNameLower: Optional[str] = Field(
        default=None,
        description="Lower than normal pattern name",
        examples=["pattern-lower"]
    )
    detectionType: Optional[str] = Field(
        default=None,
        description="Detection Type. Accepted Values - Positive, Negative, or Both",
        examples=["Positive"]
    )
    positiveBaselineViolationFactor: Optional[float] = Field(
        default=None,
        description="The baseline violation factor for higher than normal detection",
        examples=[2.0]
    )

class ComponentMetricSettingV1(BaseModel):

    apiVersion: Literal["v1"] = Field(
        ...,
        description="API Version",
        exclude=True
    )

    type: Literal["consumerMetricSetting"] = Field(
        ...,
        description="Type of configuration",
        exclude=True
    )

    metricSettings: Optional[List[MetricSetting]] = Field(
        default=None,
        description="List of instances"
    )