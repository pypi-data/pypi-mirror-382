from dataclasses import dataclass

from dots.operation import Operation
from dots.operation.target import Target


class _Sequence(Operation):
    def __init__(self, operations: [Operation]):
        self.operations = operations

    async def apply(self, target: Target):
        for operation in self.operations:
            await operation.apply(target)


def sequence(*operations) -> Operation:
    return _Sequence(operations)
