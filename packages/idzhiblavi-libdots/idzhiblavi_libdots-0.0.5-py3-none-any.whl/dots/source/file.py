from dataclasses import dataclass

from dots.operation.link_file import LinkFile
from dots.operation.copy_file import CopyFile


@dataclass
class File:
    path: str

    def link_to(self, destination: str):
        return LinkFile(
            source_path=self.path,
            destination_path=destination,
        )

    def copy_to(self, destination: str):
        return CopyFile(
            source_path=self.path,
            destination_path=destination,
        )
