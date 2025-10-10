import hashlib
import binascii
from typing import Protocol, AnyStr


_DEFAULT_HASHER = hashlib.sha256


class Hasher(Protocol):
    """A hash function, such as from `hashlib`."""

    def __init__(self, data: bytes): ...

    def digest(self, data: bytes) -> bytes: ...


def _ensure_bytes(data: AnyStr) -> bytes:
    """Ensure the data is bytes.

    Args:
        data: The data to ensure is bytes.

    Returns:
        The data as bytes.
    """
    return data.encode("utf-8") if isinstance(data, str) else data


def _hash_digest(
    hasher: Hasher,
    data: AnyStr,
    secret: AnyStr | None = None,
    n: int | None = None,
) -> bytes:
    """Generate a binary digest from a hash function.

    Args:
        hasher: The hash function to use.
        data: The data to hash.
        secret: The secret to hash with, if any.
        n: The number of bytes to return. If not provided, the full digest is returned.

    Returns:
        The binary digest. If `n` is provided, the first `n` bytes are returned.
    """
    bdata = _ensure_bytes(data)
    if secret is not None:
        bdata = _ensure_bytes(secret) + bdata
    digest = hasher(bdata).digest()
    if n is not None:
        return digest[:n]
    return digest


def _bin_to_str(bin_id: bytes) -> str:
    """Convert a binary ID to a string.

    Args:
        bin_id: The binary ID.

    Returns:
        The string ID.
    """
    return binascii.b2a_hex(bin_id).decode()


def _str_to_bin(str_id: str) -> bytes:
    """Convert a string ID to a binary ID.

    The input should be from a call to `_bin_to_str`.

    Args:
        str_id: The string ID.

    Returns:
        The binary ID.
    """
    return binascii.a2b_hex(str_id)


def signed_id(
    input_id: AnyStr,
    secret: AnyStr,
    id_bytes: int = 2,
    sig_bytes: int = 2,
    hasher: Hasher = _DEFAULT_HASHER,
) -> str:
    """Generate a stable, signed ID.

    With the same settings, the ID is unique to users via the `name_id`.
    The input ID is not obviously in the generated ID, though it could be
    reversed without much work.

    The generated ID can be verified with knowledge of the `secret` and
    the `id_bytes` and `sig_bytes` parameters.

    It is unlikely a random ID could be generated with a correct secret,
    depending on how many bytes are used.

    The `id_bytes` and `sig_bytes` parameters can be used to control the
    length of the ID and signature. Lower values mean collisions are more
    likely, and unintentionally valid signatures are more likely, but the ID is shorter.

    Args:
        input_id: The input ID.
        secret: The secret key.
        id_bytes: Bytes used from each hash for the ID.
        sig_bytes: Bytes used from each hash for the signature.
        hasher: The hash function to use.

    Returns:
        The generated ID.
    """
    # Hash the input ID and take the first `space` bytes.
    id_hash = _hash_digest(hasher, input_id, n=id_bytes)
    sig = _hash_digest(hasher, id_hash, secret=secret, n=sig_bytes)
    # Create a short, url-safe, string ID.
    return _bin_to_str(id_hash + sig)


def verify_signed_id(
    id_: str,
    secret: AnyStr,
    id_bytes: int = 2,
    sig_bytes: int = 2,
    hasher: Hasher = _DEFAULT_HASHER,
    raise_on_invalid: bool = True,
) -> bool:
    """Verify an ID generated with `signed_id`.

    Args:
        id_: The ID to verify.
        secret: The secret key.
        id_bytes: Bytes used from each hash for the ID.
        sig_bytes: Bytes used from each hash for the signature.
        hasher: The hash function to use.

    Raises:
        `ValueError`: If the ID is invalid.
    """
    # Decode the input ID.
    try:
        bin_id = _str_to_bin(id_)
    except binascii.Error:
        if raise_on_invalid:
            raise ValueError("Invalid ID.")
        return False
    input_id, input_sig = bin_id[:id_bytes], bin_id[id_bytes:]
    # Verify that the ID and signature have the same length.
    if len(input_id) != id_bytes or len(input_sig) != sig_bytes:
        if raise_on_invalid:
            raise ValueError("Invalid ID.")
        return False
    # Compute an expected signature based on the short ID hash.
    expected_sig = _hash_digest(hasher, input_id, secret=secret, n=sig_bytes)
    # Compare the beginning of the signature to the actual signature.
    valid = expected_sig == input_sig
    if raise_on_invalid and not valid:
        raise ValueError("Invalid ID.")
    return valid
