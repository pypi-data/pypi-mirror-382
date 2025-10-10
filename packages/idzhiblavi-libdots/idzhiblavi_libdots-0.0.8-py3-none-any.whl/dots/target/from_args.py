import argparse

from dots.operation.target import Target

from dots.target.noop_target import NoopTarget
from dots.target.local_target import LocalTarget
from dots.target.local_diff_target import LocalDiffTarget


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
    )

    parser.add_argument(
        "--diff",
        "-D",
        action=argparse.BooleanOptionalAction,
    )

    return parser.parse_args()


def target_from_args() -> Target:
    args = _parse_args()

    if args.diff:
        return LocalDiffTarget()

    if args.dry_run:
        return NoopTarget()

    return LocalTarget()
