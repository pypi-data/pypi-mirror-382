import secrets
from enum import StrEnum
from typing import Literal, overload
from maleo.types.bytes import OptionalBytes
from maleo.types.integer import OptionalInteger
from maleo.types.misc import BytesOrString, OptionalBytesOrString
from maleo.types.string import ListOfStrings, OptionalString


class RandomFormat(StrEnum):
    BYTES = "bytes"
    HEX = "hex"
    STRING = "string"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


@overload
def random(
    format: Literal[RandomFormat.BYTES],
    nbytes: OptionalInteger = None,
    *,
    prefix: OptionalBytes = None,
    suffix: OptionalBytes = None,
) -> bytes: ...
@overload
def random(
    format: Literal[RandomFormat.HEX, RandomFormat.STRING] = RandomFormat.STRING,
    nbytes: OptionalInteger = None,
    *,
    prefix: OptionalString = None,
    suffix: OptionalString = None,
) -> str: ...
def random(
    format: RandomFormat = RandomFormat.STRING,
    nbytes: OptionalInteger = None,
    *,
    prefix: OptionalBytesOrString = None,
    suffix: OptionalBytesOrString = None,
) -> BytesOrString:
    if format is RandomFormat.BYTES:
        token = secrets.token_bytes(nbytes)
        if prefix is not None:
            if not isinstance(prefix, bytes):
                raise ValueError("Prefix must be a bytes")
            token = prefix + token
        if suffix is not None:
            if not isinstance(suffix, bytes):
                raise ValueError("Suffix must be a bytes")
            token = token + suffix
        return token
    elif format is RandomFormat.HEX:
        token = secrets.token_hex(nbytes)
        if prefix is not None:
            if not isinstance(prefix, str):
                raise ValueError("Prefix must be a string")
            token = prefix + token
        if suffix is not None:
            if not isinstance(suffix, str):
                raise ValueError("Suffix must be a string")
            token = token + suffix
        return token
    elif format is RandomFormat.STRING:
        token = secrets.token_urlsafe(nbytes)
        if prefix is not None:
            if not isinstance(prefix, str):
                raise ValueError("Prefix must be a string")
            token = prefix + token
        if suffix is not None:
            if not isinstance(suffix, str):
                raise ValueError("Suffix must be a string")
            token = token + suffix
        return token
