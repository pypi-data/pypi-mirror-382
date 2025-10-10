import os
import fnmatch


def check_can_put_file(path: str):
    if os.path.isdir(path):
        raise RuntimeError(f"cannot put file at path {path}: is a directory")


def check_can_put_directory(path: str):
    if os.path.isfile(path):
        raise RuntimeError(f"cannot put directory at path {path}: is a file")


def softlink_exists(source, destination):
    if not os.path.islink(destination):
        return False

    return os.path.realpath(os.readlink(destination)) == os.path.realpath(source)


def make_shell_patterns_matcher(patterns):
    def matcher(name):
        return any(map(lambda pattern: fnmatch.fnmatch(name, pattern), patterns))

    return matcher
