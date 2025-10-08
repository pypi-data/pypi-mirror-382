import yaml
from typing import Any, Dict, Optional
from pydantic import BaseModel
import glob
import itertools
import os
from ifclient.config.models.common.file_reference import FileReference
from ifclient.exceptions.config import EmptyYAMLError
from ifclient.utils.file_util import load_yaml
from ifclient.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_object_from_type(data: Dict, version: str, config_type: str) -> BaseModel:

    if version == "v1":
        if config_type == "toolConfig":
            from ifclient.config.models.v1.tool_config import ToolConfigV1
            return ToolConfigV1(**data)
        if config_type == "projectBase":
            from ifclient.config.models.v1.project_base import ProjectBaseV1
            return ProjectBaseV1(**data)
        elif config_type == "instanceGroupingSetting":
            from ifclient.config.models.v1.instance_grouping import InstanceGroupingSettingV1
            return InstanceGroupingSettingV1(**data)
        elif config_type == "consumerMetricSetting":
            from ifclient.config.models.v1.component_metric import ComponentMetricSettingV1
            return ComponentMetricSettingV1(**data)
        else:
            raise ValueError(f"Unknown configuration type for v1: {config_type}")
    elif version == "v2":
        raise ValueError("v2 configuration validation is not implemented")
    else:
        raise ValueError(f"Unsupported forced version: {version}") 


def validate_main_config(file_path: str, override_version: Optional[str] = None) -> Any:
    data = load_yaml(file_path)
    version = override_version or data.get("apiVersion", None)
    config_type = data.get("type")

    return get_object_from_type(data, version, config_type)

def validate_sub_config(file_path: str, forced_version: str) -> Any:
    """
    Validate a sub configuration file using the forced version from the base config.
    """
    data = load_yaml(file_path)
    config_type = data.get("type")
    # Here we ignore any apiVersion in the file and force forced_version.
    return get_object_from_type(data=data, version=forced_version, config_type=config_type)

def validate_and_resolve(file_path: str, skip_empty_files: bool, forced_version: Optional[str] = None, is_main: bool = False) -> Any:
    """
    Validate a configuration file and its sub configurations.
    
    Use validate_main_config if is_main is True; otherwise, force sub config validation with forced_version.

    This is used to enforce a specific version config to use the same version sub-configs.
    """
    try:
        logger.debug(f"Validating file {file_path}")
        if is_main:
            validated = validate_main_config(file_path, override_version=forced_version)
            version = getattr(validated, "apiVersion", forced_version or "v1")
        else:
            if forced_version is None:
                raise ValueError("Forced version must be provided for sub configurations")
            validated = validate_sub_config(file_path, forced_version)
            version = forced_version
    except EmptyYAMLError as e:
        if skip_empty_files:
            logger.debug(f"Skipping file {file_path} as it is empty")
            return None
        else:
            raise Exception(f"{file_path} is empty. Provide a non-empty YAML file or set -e/--skip-empty-files flag")
    except Exception as e:
        raise Exception(f"Error validating file {file_path}: {e}")
    else:
        logger.debug(f"File {file_path} is valid")
        # Process any file references recursively, using the forced version for sub configs.
        validated_file_references = {
            name: value for name, value in validated.__dict__.items() if isinstance(value, FileReference)
        }
        if len(validated_file_references) > 0:
            for name, value in validated_file_references.items():
                parent_dir = os.path.dirname(file_path)
                resolved_paths = [
                    glob.glob(path if os.path.isabs(path) else os.path.abspath(os.path.join(parent_dir, path)))
                    for path in value.files
                ]
                resolved_paths_flattened = list(set(itertools.chain(*resolved_paths)))
                setattr(getattr(validated, name), 'files', resolved_paths_flattened)
                paths_to_objects_list = []
                for ref_file in resolved_paths_flattened:
                    # For sub configurations, always pass forced_version.
                    model = validate_and_resolve(ref_file, skip_empty_files, forced_version=version, is_main=False)
                    if model is not None:
                        paths_to_objects_list.append(model)
                if len(paths_to_objects_list) > 0:
                    setattr(validated, name, paths_to_objects_list)
                else:
                    setattr(validated, name, None)
            
        return validated

