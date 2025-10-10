import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_sandbox import NAME
from bluer_sandbox.village.analysis import analyze
from bluer_sandbox import env
from bluer_sandbox.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="analyze",
)
parser.add_argument(
    "--verbose",
    type=bool,
    default=0,
    help="0|1",
)
parser.add_argument(
    "--object_name",
    type=str,
    default=env.BLUER_VILLAGE_TEST_OBJECT,
)
args = parser.parse_args()

success = False
if args.task == "analyze":
    success = analyze(
        object_name=args.object_name,
        verbose=args.verbose == 1,
    )
else:
    success = None

sys_exit(logger, NAME, args.task, success)
