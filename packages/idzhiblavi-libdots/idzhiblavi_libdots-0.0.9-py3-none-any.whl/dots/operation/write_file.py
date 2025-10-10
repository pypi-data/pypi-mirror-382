from dataclasses import dataclass

from dots.operation import Operation
from dots.operation.target import Target


@dataclass
class WriteFile(Operation):
    content: str
    path: str

    async def apply(self, target: Target):
        await target.write_file(
            content=self.content,
            path=self.path,
        )
