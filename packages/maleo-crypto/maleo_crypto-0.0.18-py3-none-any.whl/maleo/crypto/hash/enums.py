from enum import StrEnum
from maleo.types.string import ListOfStrings


class Mode(StrEnum):
    DIGEST = "digest"
    OBJECT = "object"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]
