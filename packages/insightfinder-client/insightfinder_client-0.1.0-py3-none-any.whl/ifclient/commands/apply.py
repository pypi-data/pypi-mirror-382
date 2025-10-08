import click
from ifclient.config.validation.dispatcher import validate_and_resolve
from pydantic import ValidationError
from ifclient.api.client import apply_config
from ifclient.utils.file_util import find_tool_configs_in_dir
from ifclient.utils.logger import setup_logger, set_logging_level
import time
import os
import sys

@click.command(name="apply")
@click.argument("config_path", default = ".", type=click.Path(exists=True, dir_okay=True, file_okay=True)) 
@click.option("-e", "--skip-empty-files", type=bool, default=False, help="Skip empty files from validation")
@click.option("--debug/--no-debug", type=bool, default=False, help="Show debug logs")
def apply_cmd(config_path: str, skip_empty_files, debug):
    """
    Apply the configuration for all files in CONFIG_PATH for the desired projects. Default path is current directory
    """

    if debug:
        set_logging_level("DEBUG")
    else:
        set_logging_level("INFO")

    logger = setup_logger(__name__)
    try:

        # Check if path exists or not
        if not os.path.exists(config_path):
            raise Exception("Path provided doesn't exist")

        # Checking if path is file or directory and getting all tool configs if it is a directory
        abspath = os.path.abspath(config_path)

        tool_config_files = []

        if os.path.isdir(abspath):
            tool_config_files = find_tool_configs_in_dir(abspath)
        else:
            tool_config_files.append(abspath)

        if len(tool_config_files) == 0:
            logger.error("No config files found of type toolConfig. Stopping apply")
            sys.exit(1)


        for file in tool_config_files:
            
            try:

                # Validate first before applying
                validated_record = validate_and_resolve(file, skip_empty_files, is_main=True)
                logger.debug(f"Configuration is valid.")

                # Merge the configs based on values
                if getattr(validated_record, 'apiVersion') == "v1":
                    from ifclient.config.merger.v1.config_merge import config_merge
                    config = config_merge(validated_record)
                    for project in config['projects']:
                        try:
                            logger.info(f"Updating settings for project: {project['name']}")
                            apply_config(project, config['baseUrl'])
                            logger.info(f"Finished updating settings for project: {project['name']}")
                            time.sleep(3)
                        except Exception as e:
                            print(f"An exception occured: {e}")
                            print(f"Could not apply config for project {project['name']}. Skipping it")
                            time.sleep(3)
                else:
                    raise ValueError(f"This version is not yet supported for apply command")

            except ValidationError as e:
                logger.error(f"Validation error: {e}")
                logger.error(f"Validation failed for {file}. Skipping it")
    except Exception as e:
        logger.error(f"Exception: {e}")
        sys.exit(1)