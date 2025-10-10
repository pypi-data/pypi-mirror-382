from typing import List

from bluer_options.terminal import show_usage, xtra


def help_analyze(
    tokens: List[str],
    mono: bool,
) -> str:
    options = xtra("~download,dryrun,upload", mono=mono)

    args = [
        "[--verbose 1]",
    ]

    return show_usage(
        [
            "@village",
            "analyze",
            f"[{options}]",
            "[.|$BLUER_VILLAGE_TEST_OBJECT]",
        ]
        + args,
        "analyze village.",
        mono=mono,
    )


help_functions = {
    "analyze": help_analyze,
}
