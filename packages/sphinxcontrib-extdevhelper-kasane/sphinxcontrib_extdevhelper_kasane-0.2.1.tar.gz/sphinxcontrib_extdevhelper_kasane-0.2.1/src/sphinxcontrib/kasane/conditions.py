from typing import Protocol

from sphinx.builders import Builder


class BuilderCondition(Protocol):
    def is_satisfied_by(self, builder: Builder) -> bool: ...


class BuilderFormatCondition:
    def __init__(self, format: str) -> None:
        self.format = format

    def is_satisfied_by(self, builder: Builder) -> bool:
        return builder.format == self.format


class BuilderNameCondition:
    def __init__(self, name: str) -> None:
        self.name = name

    def is_satisfied_by(self, builder: Builder) -> bool:
        return builder.name == self.name
