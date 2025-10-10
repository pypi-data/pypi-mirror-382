class Target:
    async def write_file(self, content: str, path: str):
        raise NotImplementedError()

    async def create_softlink(self, source: str, destination: str):
        raise NotImplementedError()

    async def copy_file(self, source: str, destination: str):
        raise NotImplementedError()

    async def copy_directory(self, source: str, destination: str, ignore: [str]):
        raise NotImplementedError()
