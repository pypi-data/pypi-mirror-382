import asyncio

from dataclasses import dataclass

from dots.operation import Operation
from dots.operation.target import Target


class _All(Operation):
    def __init__(self, operations: [Operation]):
        self.operations = operations

    async def apply(self, target: Target):
        await asyncio.gather(
            *[
                asyncio.create_task(operation.apply(target))
                for operation in self.operations
            ],
        )


def all(*operations) -> Operation:
    return _All(operations)
