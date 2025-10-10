from dataclasses import dataclass, field

from dots.operation.link_directory import LinkDirectory
from dots.operation.copy_directory import CopyDirectory


@dataclass
class Directory:
    path: str
    ignore: [str] = field(default_factory=lambda: [".git"])

    def link_to(self, destination: str):
        return LinkDirectory(
            source_path=self.path,
            destination_path=destination,
        )

    def copy_to(self, destination: str):
        return CopyDirectory(
            source_path=self.path,
            destination_path=destination,
            ignore=self.ignore,
        )
