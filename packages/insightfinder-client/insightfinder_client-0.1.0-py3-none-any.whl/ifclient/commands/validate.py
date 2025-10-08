import click
from ifclient.config.validation.dispatcher import validate_and_resolve
from pydantic import ValidationError
import os
from ifclient.utils.file_util import find_tool_configs_in_dir
from ifclient.utils.logger import setup_logger, set_logging_level
import sys

@click.command(name="validate")
@click.argument("config_path", type=click.Path(exists=True, dir_okay=True, file_okay=True)) 
@click.option("-e", "--skip-empty-files", type=bool, default=False, help="Skip empty files from validation")
@click.option("--debug/--no-debug", type=bool, default=False, help="Show debug logs")
def validate_cmd(config_path, skip_empty_files, debug):
    """
    Validate the provided configuration file(s) recursively (and all referenced files).
    If CONFIG_PATH is a directory all tool configs from that directory are validated along with their references
    If CONFIG_PATH is a file only that file is validated along with its references
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

        config_files = []

        if os.path.isdir(abspath):
            config_files = find_tool_configs_in_dir(abspath)
        else:
            config_files.append(abspath)

        if len(config_files) == 0:
            logger.error(f"No config files found for the given path: {config_path}")
            return
        
        for file in config_files:

            has_error = False

            try:
                validated_record = validate_and_resolve(file, skip_empty_files, is_main=True)
                if validated_record:
                    logger.debug(validated_record.model_dump_json(indent=4))
                    logger.info(f"Configuration is valid for file: {file}.")
            except ValidationError as e:
                logger.error(f"Validation error: {e}")
                logger.error(f"Validation failed for file: {file}")
                has_error = True
        
        if has_error:
            logger.error("Validation failed for some files")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Exception: {e}")
        sys.exit(1)
