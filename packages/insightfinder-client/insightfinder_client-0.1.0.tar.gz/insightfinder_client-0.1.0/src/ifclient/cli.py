# client/cli.py
import click
from ifclient.commands import validate, plan, generate, apply
from dotenv import load_dotenv

@click.group()
def cli():
    """A CLI tool for managing configurations and applying API calls."""

    load_dotenv()

cli.add_command(validate.validate_cmd)
# cli.add_command(plan.plan_cmd)
cli.add_command(generate.generate_cmd)
cli.add_command(apply.apply_cmd)

if __name__ == '__main__':
    cli()
