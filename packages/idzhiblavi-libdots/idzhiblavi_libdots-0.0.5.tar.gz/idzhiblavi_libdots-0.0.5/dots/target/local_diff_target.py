import os
import re
import filecmp
import fnmatch
import difflib

import aiofile
from loguru import logger

from dots.operation.target import Target
from dots.target import util
from dots.target import log
from dots.util.read_file import read_file


async def _print_files_diff(a, b):
    c_a = await read_file(a)
    c_b = await read_file(b)
    return _print_lines_diff(c_a.splitlines(), c_b.splitlines(), a, b)


def _print_lines_diff(a, b, path_a, path_b):
    diff = list(difflib.unified_diff(a, b, path_a, path_b))
    if not diff:
        return

    logger.info(f"files {path_a} and {path_b} differ:")
    print("\n".join(diff))


class LocalDiffTarget(Target):
    async def write_file(self, content: str, path: str):
        util.check_can_put_file(path)

        if not os.path.exists(path):
            path_content = []
        else:
            path_content = await read_file(path)

        _print_lines_diff(
            path_content.splitlines(),
            content.splitlines(),
            path,
            "<generated>",
        )

    async def create_softlink(self, source: str, destination: str):
        if util.softlink_exists(source, destination):
            return

        if os.path.exists(destination):
            logger.info(f"--- remove {destination}")

        logger.info(f"+++ softlink {destination} -> {source}")

    async def copy_file(self, source: str, destination: str):
        util.check_can_put_file(destination)
        _print_files_diff(destination, source)

    async def copy_directory(self, source: str, destination: str, ignore: list[str]):
        util.check_can_put_directory(destination)
        ignored = util.make_shell_patterns_matcher(patterns=ignore)
        cmp = filecmp.dircmp(source, destination, shallow=False)
        await self._report(cmp, ignored)

    async def _report(self, cmp: filecmp.dircmp, ignored):
        for p in cmp.diff_files:
            if ignored(p):
                self._log_ignored(cmp.left, p)
            else:
                await _print_files_diff(f"{cmp.right}/{p}", f"{cmp.left}/{p}")

        for p in cmp.funny_files:
            if ignored(p):
                self._log_ignored(cmp.left, p)
            else:
                logger.warning(f"unknown file state, skip: {cmp.left}/{p}")

        for p in cmp.left_only:
            if ignored(p):
                self._log_ignored(cmp.left, p)
            else:
                logger.info(f"file will be added: {cmp.right}/{p}")

        for p in cmp.right_only:
            if ignored(p):
                self._log_ignored(cmp.right, p)
            else:
                logger.info(f"file will be removed: {cmp.right}/{p}")

        for dir, sub_cmp in cmp.subdirs.items():
            if ignored(dir):
                self._log_ignored(cmp.left, dir)
            else:
                await self._report(sub_cmp, ignored)

    def _log_ignored(self, dir, path):
        logger.info(f"path is ignored: {dir}/{path}")
