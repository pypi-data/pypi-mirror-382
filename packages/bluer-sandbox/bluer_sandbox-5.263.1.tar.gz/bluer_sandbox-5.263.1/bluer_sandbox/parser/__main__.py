import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_sandbox import NAME
from bluer_sandbox.parser.parsing import parse
from bluer_sandbox.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="parse",
)
parser.add_argument(
    "--object_name",
    type=str,
)
parser.add_argument(
    "--filename",
    type=str,
    default="",
)
parser.add_argument(
    "--url",
    type=str,
)
args = parser.parse_args()

success = False
if args.task == "parse":
    success, _ = parse(
        url=args.url,
        object_name=args.object_name,
        filename=args.filename,
    )
else:
    success = None

sys_exit(logger, NAME, args.task, success)
