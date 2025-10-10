from dataclasses import dataclass

from dots.operation.write_file import WriteFile


@dataclass
class String:
    value: str

    def write_to(self, path: str):
        return WriteFile(
            content=self.value,
            path=path,
        )
