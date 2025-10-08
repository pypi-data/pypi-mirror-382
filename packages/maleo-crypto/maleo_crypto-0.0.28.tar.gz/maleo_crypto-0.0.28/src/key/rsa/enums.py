from enum import StrEnum
from maleo.types.string import ListOfStrings


class KeyType(StrEnum):
    PRIVATE = "private"
    PUBLIC = "public"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


class Loader(StrEnum):
    CRYPTOGRAPHY = "cryptography"
    PYCRYPTODOME = "pycryptodome"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]
