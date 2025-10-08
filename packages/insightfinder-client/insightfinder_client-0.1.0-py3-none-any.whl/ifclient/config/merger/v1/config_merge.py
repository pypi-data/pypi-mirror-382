from ifclient.config.models.v1.tool_config import ToolConfigV1
from ifclient.config.models.v1.project_base import ProjectBaseV1
from ifclient.config.models.v1.instance_grouping import InstanceGroupingSettingV1, InstanceGrouping
from ifclient.config.models.v1.component_metric import ComponentMetricSettingV1, MetricSetting
from typing import Dict, Any, List
from itertools import chain
import json
from ifclient.utils.logger import setup_logger

logger = setup_logger(__name__)

def config_merge(tool_config: ToolConfigV1) -> Dict[str, Any]:

    try:

        if tool_config.projectBaseConfigs is None:
            logger.info("No projects to apply or generate configurations for. Exiting")
            return None

        project_configs = []

        for project in tool_config.projectBaseConfigs:
            
            assert(isinstance(project, ProjectBaseV1))

            """
            Converting instanceGroupingUpdate to the required InstanceGrouping type schema
            This should only be done when instanceGroupingUpdate is a List. Indicates that it is a list of InstanceGroupingSettingV1.
            """          
            if project.instanceGroupingUpdate and isinstance(project.instanceGroupingUpdate, List) and all(isinstance(x, InstanceGroupingSettingV1) for x in project.instanceGroupingUpdate):

                final_instances_list = list(chain.from_iterable([x.instanceDataList for x in project.instanceGroupingUpdate]))

                final_instance_grouping = InstanceGrouping(instanceDataList=final_instances_list)

                project.instanceGroupingUpdate = final_instance_grouping

            """
            Converting componentMetricSettingOverallModelList to the list of MetricSetting schema
            This should only be done when instanceGroupingUpdate is a List. Indicates that it is a list of InstanceGroupingSettingV1.
            """          
            if project.componentMetricSettingOverallModelList and isinstance(project.componentMetricSettingOverallModelList, List) and all(isinstance(x, ComponentMetricSettingV1) for x in project.componentMetricSettingOverallModelList):
                
                final_metric_settings_list = list(chain.from_iterable([x.metricSettings for x in project.componentMetricSettingOverallModelList]))

                project.componentMetricSettingOverallModelList = final_metric_settings_list


            project_dict = json.loads(project.model_dump_json(exclude_none=True))

            del project_dict['project']
            del project_dict['userName']

            record = dict()
            record['name'] = project.project
            record['userName'] = project.userName
            record['data'] = project_dict

            project_configs.append(record)
        
        config = dict()
        config['baseUrl'] = str(tool_config.baseUrl)
        config['projects'] = project_configs
        return config

    except Exception as e:
        logger.error("An exception occured while merging the configurations")
        raise e
