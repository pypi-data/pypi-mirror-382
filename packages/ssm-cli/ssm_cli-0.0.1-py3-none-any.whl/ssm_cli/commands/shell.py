from ssm_cli.instances import Instances
from ssm_cli.commands.base import BaseCommand
from ssm_cli.cli_args import ARGS

import logging
logger = logging.getLogger(__name__)


class ShellCommand(BaseCommand):
    HELP = "Connects to instances"
    
    def add_arguments(parser):
        parser.add_argument("group", type=str, help="group to run against")

    def run():
        logger.info("running shell action")

        instances = Instances()
        instance = instances.select_instance(ARGS.group, "tui")

        if instance is None:
            logger.error("failed to select host")
            raise RuntimeError("failed to select host")

        logger.info(f"connecting to {repr(instance)}")
        
        instance.start_session()