from dots.operation.target import Target
from dots.target import log


class NoopTarget(Target):
    def __init__(self):
        pass

    async def write_file(self, content: str, path: str):
        log.wrote_content(path)

    async def create_softlink(self, source: str, destination: str):
        log.softlink_created(source, destination)

    async def copy_file(self, source: str, destination: str):
        log.file_copied(source, destination)

    async def copy_directory(self, source: str, destination: str, ignore: [str]):
        log.directory_copied(source, destination)
