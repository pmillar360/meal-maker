from datetime import datetime, timedelta, timezone
import os
import subprocess
import sys

import jwt
import pytest

from util import auth


@pytest.mark.parametrize("create_token", [auth.create_access_token, auth.create_refresh_token])
def test_token_round_trip(create_token):
    token = create_token({"sub": "test-user"})

    payload = auth.verify_token(token)

    assert payload is not None
    assert payload["sub"] == "test-user"
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()


@pytest.mark.parametrize("algorithm", ["HS384", "HS512", "none"])
def test_rejects_disallowed_algorithm(algorithm, monkeypatch):
    monkeypatch.setattr(auth, "SECRET_KEY", "algorithm-rejection-test-key-" * 3)
    key = None if algorithm == "none" else auth.SECRET_KEY
    token = jwt.encode({"sub": "test-user"}, key, algorithm=algorithm)

    assert auth.verify_token(token) is None


def test_rejects_expired_token():
    token = jwt.encode(
        {"sub": "test-user", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        auth.SECRET_KEY,
        algorithm="HS256",
    )

    assert auth.verify_token(token) is None


def test_rejects_invalid_signature():
    token = jwt.encode({"sub": "test-user"}, "different-test-signing-key-at-least-32-bytes", algorithm="HS256")

    assert auth.verify_token(token) is None


def test_rejects_malformed_token():
    assert auth.verify_token("not-a-jwt") is None


def test_accepts_existing_python_jose_token(monkeypatch):
    monkeypatch.setattr(auth, "SECRET_KEY", "legacy-compatibility-test-secret-key")
    # Generated with python-jose 3.5.0 using the test key above.
    token = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiJsZWdhY3ktdXNlciIsImV4cCI6NDEwMjQ0NDgwMH0."
        "fG2jC0wqRTymZqGbIofD2brOIReWid-V8mvhgvn1D4I"
    )

    assert auth.verify_token(token) == {"sub": "legacy-user", "exp": 4102444800}


@pytest.mark.parametrize("secret", [None, ""])
def test_startup_requires_secret(secret):
    env = os.environ.copy()
    env["PYTHON_DOTENV_DISABLED"] = "1"
    env["DATABASE_URL"] = "sqlite:///:memory:"
    if secret is None:
        env.pop("SECRET_KEY", None)
    else:
        env["SECRET_KEY"] = secret

    result = subprocess.run(
        [sys.executable, "-c", "import app.main"],
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "SECRET_KEY must be configured" in result.stderr
