import glob
import yaml
import os
from ifclient.exceptions.config import EmptyYAMLError
from typing import Dict, Any
from ifclient.utils.logger import setup_logger

logger = setup_logger(__name__)


def load_yaml(file_path: str) -> Dict[str, Any]:

    with open(file_path, 'r') as f:
        content = f.read()
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as e:
        raise e
    else:
        if data is None:
            raise EmptyYAMLError(f"File {file_path} is an empty yaml file")
        else:
            return data

def find_tool_configs_in_dir(dir: str):

    files = glob.glob(os.path.join(dir, "*.yaml"))
    tool_config_files = list()

    for file in files:

        try:
            data = load_yaml(file)
            if data and 'type' in data and data['type'] == 'toolConfig':
                tool_config_files.append(file)

        except EmptyYAMLError:
            logger.debug("Skipping empty yaml file")
        
        except Exception as e:
            raise e
        
    
    return tool_config_files
