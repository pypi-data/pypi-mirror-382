import asyncio

from dots.operation import Operation
from dots.operation.target import Target

from dots.util.run_sync import run_sync


async def apply_all(operations: [Operation], target: Target):
    await asyncio.gather(
        *[asyncio.create_task(operation.apply(target)) for operation in operations],
    )


def apply_all_sync(operations: [Operation], target: Target):
    run_sync(apply_all(operations, target))
