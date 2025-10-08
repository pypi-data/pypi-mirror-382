from enum import StrEnum
from maleo.types.string import ListOfStrings


class Format(StrEnum):
    BYTES = "bytes"
    STRING = "string"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]
