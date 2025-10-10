from dots.operation.target import Target


class Operation:
    async def apply(self, target: Target):
        raise NotImplementedError()
