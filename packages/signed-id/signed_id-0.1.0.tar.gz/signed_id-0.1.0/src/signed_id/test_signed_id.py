import pytest
import hashlib

from .signed_id import signed_id, verify_signed_id


@pytest.mark.parametrize(
    "input_id, secret, expected_id",
    [
        ("test", "secret", "9f862490"),
        (b"test", b"secret", "9f862490"),
        (b"test", "secret", "9f862490"),
        ("test", b"secret", "9f862490"),
    ],
)
def test_signed_id_defaults(input_id, secret, expected_id):
    assert signed_id(input_id, secret) == expected_id


@pytest.mark.parametrize(
    "input_id, secret, id_bytes, sig_bytes, hasher, expected_id",
    [
        ("test", "secret", 2, 2, hashlib.sha256, "9f862490"),
        (b"test", b"secret", 2, 2, hashlib.sha256, "9f862490"),
        (b"test", "secret", 2, 2, hashlib.sha256, "9f862490"),
        ("test", b"secret", 2, 2, hashlib.sha256, "9f862490"),
        ("test", "different secret", 2, 2, hashlib.sha256, "9f86328b"),
        ("test", "secret", 4, 2, hashlib.sha256, "9f86d08159d1"),
        ("test", "secret", 2, 4, hashlib.sha256, "9f8624903db8"),
        ("test", "secret", 4, 4, hashlib.sha256, "9f86d08159d19734"),
        ("test", "secret", 2, 2, hashlib.sha512, "ee267fcc"),
        ("", "", 2, 2, hashlib.sha256, "e3b09009"),
    ],
)
def test_signed_id(input_id, secret, id_bytes, sig_bytes, hasher, expected_id):
    assert signed_id(input_id, secret, id_bytes, sig_bytes, hasher) == expected_id


@pytest.mark.parametrize(
    "id_, secret, expected_valid",
    [
        ("9f862490", "secret", True),
        ("9f862491", "secret", False),
    ],
)
def test_verify_signed_id_defaults(id_, secret, expected_valid):
    if expected_valid:
        assert verify_signed_id(id_, secret) == expected_valid
    else:
        # If the expectation is to fail, test both with and without the raise_on_invalid flag.
        with pytest.raises(ValueError):
            verify_signed_id(id_, secret)
        assert verify_signed_id(id_, secret, raise_on_invalid=False) == expected_valid


@pytest.mark.parametrize(
    "id_, secret, id_bytes, sig_bytes, hasher, expected_valid",
    [
        ("9f862490", "secret", 2, 2, hashlib.sha256, True),
        ("9f862491", "secret", 2, 2, hashlib.sha256, False),
        ("9f862490", "different secret", 2, 2, hashlib.sha256, False),
        ("9f862490", "different secret", 2, 2, hashlib.sha256, False),
        ("9f862490", "secret", 2, 1, hashlib.sha256, False),
        ("9f862490", "secret", 1, 2, hashlib.sha256, False),
        ("mmmmmmmm", "secret", 2, 2, hashlib.sha256, False),
        ("ee267fcc", "secret", 2, 2, hashlib.sha512, True),
    ],
)
def test_verify_signed_id(id_, secret, id_bytes, sig_bytes, hasher, expected_valid):
    if expected_valid:
        assert (
            verify_signed_id(id_, secret, id_bytes, sig_bytes, hasher) == expected_valid
        )
    else:
        # If the expectation is to fail, test both with and without the raise_on_invalid flag.
        with pytest.raises(ValueError):
            verify_signed_id(id_, secret, id_bytes, sig_bytes, hasher)
        assert (
            verify_signed_id(
                id_, secret, id_bytes, sig_bytes, hasher, raise_on_invalid=False
            )
            == expected_valid
        )
