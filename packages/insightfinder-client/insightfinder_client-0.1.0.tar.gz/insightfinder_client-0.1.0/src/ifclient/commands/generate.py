import click
from ifclient.config.validation.dispatcher import validate_and_resolve
from pydantic import ValidationError
import yaml
import sys
from ifclient.utils.logger import setup_logger, set_logging_level


@click.command(name="generate")
@click.argument("config_file", type=click.Path(exists=True, dir_okay=False)) 
@click.option("-e", "--skip-empty-files", type=bool, default=False, help="Skip empty files from validation")
@click.argument("output_file", type=click.File("w"), required=False)
@click.option("--debug/--no-debug", type=bool, default=False, help="Show debug logs")
def generate_cmd(config_file, skip_empty_files, output_file, debug):
    """
    Generate a yaml file as ouput combining all project configurations after resolving.
    Accepts CONFIG_FILE of type toolConfig and an OUTPUT_FILE to write the data to. '-' to output to stdout
    """


    if debug:
        set_logging_level("DEBUG")
    else:
        set_logging_level("INFO")

    logger = setup_logger(__name__)

    try:
        # Validate first before applying
        validated_record = validate_and_resolve(config_file, skip_empty_files, is_main=True)
        logger.debug(f"Configuration is valid.")

        if not getattr(validated_record, 'type') == 'toolConfig':
            raise Exception("Cannot generate data for file which is not of type toolConfig")

        # Merge the configs based on values
        if getattr(validated_record, 'apiVersion') == "v1":
            from ifclient.config.merger.v1.config_merge import config_merge
            config = config_merge(validated_record)
            if not output_file:
                stream = sys.stdout
            else:
                stream = output_file
            yaml.dump_all(config['projects'], stream, indent=2)
        else:
            raise ValueError(f"This version is not yet supported")

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Exception: {e}")
        sys.exit(1)