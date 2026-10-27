"""Tests for password hashing and JWT tokens.

Security code gets the most tests: we check that the right thing works AND
that every wrong thing (bad password, expired token, forged token) is rejected.
"""

from datetime import timedelta

import jwt
import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)

# --- Passwords ---------------------------------------------------------------


def test_hash_is_not_the_password() -> None:
    hashed = hash_password("correct horse battery staple")

    assert hashed != "correct horse battery staple"
    assert hashed.startswith("$argon2id$")


def test_same_password_gives_different_hashes() -> None:
    # Each hash gets a random "salt", so two users with the same password
    # still get different hashes, and precomputed lookup tables are useless.
    assert hash_password("same-password") != hash_password("same-password")


def test_verify_accepts_right_password_and_rejects_wrong_one() -> None:
    hashed = hash_password("s3cret-Pass!")

    assert verify_password("s3cret-Pass!", hashed) is True
    assert verify_password("s3cret-pass!", hashed) is False  # case matters


def test_verify_returns_false_for_garbage_hash() -> None:
    assert verify_password("anything", "not-a-real-hash") is False


# --- JWT tokens ----------------------------------------------------------------


def test_token_round_trip() -> None:
    token = create_access_token(subject="42", role="analyst")

    payload = decode_access_token(token)

    assert payload["sub"] == "42"
    assert payload["role"] == "analyst"


def test_expired_token_is_rejected() -> None:
    token = create_access_token(subject="42", role="analyst", expires_delta=timedelta(seconds=-1))

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_forged_admin_token_is_rejected() -> None:
    # An attacker makes their own "admin" token but doesn't know our secret.
    forged = jwt.encode(
        {"sub": "42", "role": "admin", "exp": 9999999999},
        "attacker-guessed-secret-key-0123456789-abcdef",
        algorithm="HS256",
    )

    with pytest.raises(jwt.InvalidSignatureError):
        decode_access_token(forged)


def test_garbage_token_is_rejected() -> None:
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("not.a.token")
