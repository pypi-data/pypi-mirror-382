from dataclasses import dataclass

from dots.operation import Operation
from dots.operation.target import Target


@dataclass
class LinkDirectory(Operation):
    source_path: str
    destination_path: str

    async def apply(self, target: Target):
        await target.create_softlink(
            source=self.source_path,
            destination=self.destination_path,
        )
