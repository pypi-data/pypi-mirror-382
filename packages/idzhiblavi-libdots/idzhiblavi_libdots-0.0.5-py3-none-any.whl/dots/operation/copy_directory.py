from dataclasses import dataclass

from dots.operation import Operation
from dots.operation.target import Target


@dataclass
class CopyDirectory(Operation):
    source_path: str
    destination_path: str
    ignore: [str]

    async def apply(self, target: Target):
        await target.copy_directory(
            source=self.source_path,
            destination=self.destination_path,
            ignore=self.ignore,
        )
