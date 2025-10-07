import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_algo import NAME
from bluer_algo.tracker.functions import track
from bluer_algo.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="track",
)
parser.add_argument(
    "--algo",
    type=str,
    help="camshift | meanshift.",
    default="camshift",
)
parser.add_argument(
    "--source",
    type=str,
    help="path to video file | camera.",
)
parser.add_argument(
    "--frame_count",
    type=int,
    default=-1,
    help="-1: all",
)
parser.add_argument(
    "--log",
    type=int,
    default=0,
    help="0 | 1",
)
parser.add_argument(
    "--verbose",
    type=int,
    default=0,
    help="0 | 1",
)
parser.add_argument(
    "--show_gui",
    type=int,
    default=0,
    help="0 | 1",
)
parser.add_argument(
    "--title",
    type=str,
    default="tracker",
)
parser.add_argument(
    "--object_name",
    type=str,
)
args = parser.parse_args()

success = False
if args.task == "track":
    success = track(
        source=args.source,
        object_name=args.object_name,
        algo=args.algo,
        frame_count=args.frame_count,
        log=args.log == 1,
        verbose=args.verbose == 1,
        show_gui=args.show_gui == 1,
        title=args.title,
    )
else:
    success = None

sys_exit(logger, NAME, args.task, success)
