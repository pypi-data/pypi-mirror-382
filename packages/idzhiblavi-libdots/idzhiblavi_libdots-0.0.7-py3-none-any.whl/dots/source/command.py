import subprocess

from dataclasses import dataclass, field
from dots.operation.write_file import WriteFile


@dataclass
class Command:
    command: [str]

    def write_to(self, destination: str):
        return WriteFile(
            content=self._run(),
            path=destination,
        )

    def _run(self):
        return str(subprocess.check_output(self.command))
