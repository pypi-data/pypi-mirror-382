import os
import aiofile


async def read_file(path: str) -> str:
    if not os.path.exists(path):
        raise RuntimeError(f"file does not exist: {path}")

    async with aiofile.async_open(path, "r") as file:
        return await file.read()
