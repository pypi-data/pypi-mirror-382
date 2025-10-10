import os
import aiofile
import shutil
import filecmp

from loguru import logger

from dots.operation.target import Target
from dots.target import util
from dots.target import log


class LocalTarget(Target):
    async def write_file(self, content: str, path: str):
        util.check_can_put_file(path)
        self._create_parent_dir_if_not_exists(path)

        async with aiofile.async_open(path, "w") as file:
            await file.write(content)

        log.wrote_content(path)

    async def create_softlink(self, source: str, destination: str):
        if util.softlink_exists(source, destination):
            logger.info(f"softlink {destination} -> {source} already exists")
            return

        self._create_parent_dir_if_not_exists(destination)

        if os.path.exists(destination):
            logger.info(f"removing {destination}")
            self._remove(destination)

        os.symlink(os.path.abspath(source), destination)
        log.softlink_created(source, destination)

    async def copy_file(self, source: str, destination: str):
        util.check_can_put_file(destination)
        self._create_parent_dir_if_not_exists(destination)
        shutil.copy(source, destination)
        log.file_copied(source, destination)

    async def copy_directory(self, source: str, destination: str, ignore: [str]):
        util.check_can_put_directory(destination)
        self._create_parent_dir_if_not_exists(destination)
        shutil.copytree(
            source,
            destination,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(*ignore),
        )
        log.directory_copied(source, destination)
        self._ensure_same_directories(
            filecmp.dircmp(source, destination, shallow=False),
            ignored=util.make_shell_patterns_matcher(ignore),
        )

    def _create_parent_dir_if_not_exists(self, target_path):
        directory = os.path.dirname(os.path.abspath(target_path))
        if os.path.exists(directory):
            return

        os.makedirs(directory, exist_ok=True)
        logger.info(f"created a parent directory: {directory}")

    def _ensure_same_directories(self, cmp: filecmp.dircmp, ignored):
        for p in cmp.diff_files:
            if ignored(p):
                self._log_ignored(cmp.left, p)
            else:
                logger.warning(f"copied file is somehow different: {cmp.left}/{p}")

        for p in cmp.funny_files:
            if ignored(p):
                self._log_ignored(cmp.left, p)
            else:
                logger.warning(f"unknown file state, skip: {cmp.left}/{p}")

        for p in cmp.left_only:
            if ignored(p):
                self._log_ignored(cmp.left, p)
            else:
                logger.warning(
                    f"missing path in destination directory: {cmp.right}/{p}",
                )

        for p in cmp.right_only:
            if ignored(p):
                self._log_ignored(cmp.right, p)
            else:
                self._remove(f"{cmp.right}/{p}")

        for dir, sub_cmp in cmp.subdirs.items():
            if ignored(dir):
                self._log_ignored(cmp.left, dir)
            else:
                self._ensure_same_directories(sub_cmp, ignored)

    def _log_ignored(self, dir, path):
        logger.info(f"path is ignored: {dir}/{path}")

    def _remove(self, path):
        logger.info(f"removing path {path}")

        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.islink(path):
            os.unlink(path)
