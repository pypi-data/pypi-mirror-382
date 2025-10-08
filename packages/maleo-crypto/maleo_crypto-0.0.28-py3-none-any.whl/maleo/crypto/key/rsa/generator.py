from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from pydantic import Field, validate_call
from typing import Annotated, Literal, Tuple, Union, overload
from maleo.types.bytes import OptionalBytes
from maleo.types.misc import (
    BytesOrString,
    OptionalBytesOrString,
)
from maleo.types.string import OptionalString
from ..enums import Format


@overload
def generate_private(
    format: Literal[Format.BYTES],
    *,
    size: Annotated[
        int, Field(ge=2048, le=8192, multiple_of=1024, description="Key's size")
    ] = 2048,
    password: OptionalBytes = None,
) -> bytes: ...
@overload
def generate_private(
    format: Literal[Format.STRING] = Format.STRING,
    *,
    size: Annotated[
        int, Field(ge=2048, le=8192, multiple_of=1024, description="Key's size")
    ] = 2048,
    password: OptionalString = None,
) -> str: ...
@validate_call
def generate_private(
    format: Format = Format.STRING,
    *,
    size: Annotated[
        int, Field(ge=2048, le=8192, multiple_of=1024, description="Key's size")
    ] = 2048,
    password: OptionalBytesOrString = None,
) -> BytesOrString:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=size,
        backend=default_backend(),
    )

    if password is None:
        encryption_algorithm = serialization.NoEncryption()
    else:
        if isinstance(password, str):
            password = password.encode()
        encryption_algorithm = serialization.BestAvailableEncryption(password)

    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm,
    )

    if format is Format.BYTES:
        return private_key_bytes

    if format is Format.STRING:
        return private_key_bytes.decode()


@overload
def generate_public(
    format: Literal[Format.BYTES], *, private: bytes, password: OptionalBytes = None
) -> bytes: ...
@overload
def generate_public(
    format: Literal[Format.STRING] = Format.STRING,
    *,
    private: str,
    password: OptionalString = None,
) -> str: ...
def generate_public(
    format: Format = Format.STRING,
    *,
    private: BytesOrString,
    password: OptionalBytesOrString = None,
) -> BytesOrString:
    if isinstance(private, str):
        private = private.encode()

    if isinstance(password, str):
        password = password.encode()

    private_key = serialization.load_pem_private_key(
        private, password, backend=default_backend()
    )

    public_key = private_key.public_key()

    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    if format is Format.BYTES:
        return public_key_bytes

    elif format is Format.STRING:
        return public_key_bytes.decode()


@overload
def generate_pair(
    format: Literal[Format.BYTES],
    *,
    size: Annotated[
        int, Field(ge=2048, le=8192, multiple_of=1024, description="Key's size")
    ] = 2048,
    password: OptionalBytes = None,
) -> Tuple[bytes, bytes]: ...
@overload
def generate_pair(
    format: Literal[Format.STRING] = Format.STRING,
    *,
    size: Annotated[
        int, Field(ge=2048, le=8192, multiple_of=1024, description="Key's size")
    ] = 2048,
    password: OptionalString = None,
) -> Tuple[str, str]: ...
@validate_call
def generate_pair(
    format: Format = Format.STRING,
    *,
    size: Annotated[
        int, Field(ge=2048, le=8192, multiple_of=1024, description="Key's size")
    ] = 2048,
    password: OptionalBytesOrString = None,
) -> Union[Tuple[bytes, bytes], Tuple[str, str]]:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=size,
        backend=default_backend(),
    )

    if password is None:
        encryption_algorithm = serialization.NoEncryption()
    else:
        if isinstance(password, str):
            password = password.encode()
        encryption_algorithm = serialization.BestAvailableEncryption(password)

    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm,
    )

    public_key = private_key.public_key()

    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    if format is Format.BYTES:
        return (private_key_bytes, public_key_bytes)

    if format is Format.STRING:
        return (private_key_bytes.decode(), public_key_bytes.decode())
