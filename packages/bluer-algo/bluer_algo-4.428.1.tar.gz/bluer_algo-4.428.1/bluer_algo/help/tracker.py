from typing import List

from bluer_options.terminal import show_usage, xtra


def help_tracker(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "".join(
        [
            "algo=camshift|meanshift,camera",
            xtra(",~download,dryrun,sandbox,", mono=mono),
            "upload",
        ]
    )

    args = [
        "[--frame_count <10>]",
        "[--log 1]",
        "[--show_gui 1]",
        "[--verbose 1]",
    ]

    return show_usage(
        [
            "@algo",
            "tracker",
            f"[{options}]",
            "[-|<object-name>]",
        ]
        + args,
        "run algo.",
        mono=mono,
    )
