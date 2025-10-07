import os

from bluer_options.help.functions import get_help
from bluer_objects import file, README

from bluer_algo import NAME, VERSION, ICON, REPO_NAME
from bluer_algo.help.functions import help_functions
from bluer_algo.README import image_classifier, socket, tracker, yolo, alias
from bluer_algo.README.items import items


def build():
    return all(
        README.build(
            items=readme.get("items", []),
            path=os.path.join(file.path(__file__), readme["path"]),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
            help_function=lambda tokens: get_help(
                tokens,
                help_functions,
                mono=True,
            ),
        )
        for readme in [
            {"path": "../docs"},
            {"path": "../..", "items": items},
        ]
        + image_classifier.docs
        + socket.docs
        + tracker.docs
        + yolo.docs
        + alias.docs
    )
