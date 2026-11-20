import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError


BACKEND_DIR = Path(__file__).resolve().parents[1]
LEGACY_REVISION = "7bd3a31eecbf"


@pytest.fixture(params=["sqlite", "postgresql"])
def migration_database(request, tmp_path):
    env = os.environ.copy()
    if request.param == "sqlite":
        url = f"sqlite:///{(tmp_path / 'migration.db').as_posix()}"
        engine = create_engine(url)
        try:
            yield engine, {**env, "DATABASE_URL": url}
        finally:
            engine.dispose()
        return

    url = os.environ.get("TEST_POSTGRES_MIGRATION_URL")
    if not url:
        pytest.skip("Set TEST_POSTGRES_MIGRATION_URL to run PostgreSQL migrations")

    schema = f"migration_test_{uuid4().hex}"
    options = f"-c search_path={schema}"
    database_url = make_url(url)
    if database_url.drivername == "postgresql":
        database_url = database_url.set(drivername="postgresql+psycopg2")
    admin_engine = create_engine(database_url)
    engine = create_engine(database_url, connect_args={"options": options})
    try:
        with admin_engine.begin() as connection:
            connection.execute(text(f"CREATE SCHEMA {schema}"))
        try:
            yield engine, {**env, "DATABASE_URL": url, "PGOPTIONS": options}
        finally:
            engine.dispose()
            with admin_engine.begin() as connection:
                connection.execute(text(f"DROP SCHEMA {schema} CASCADE"))
    finally:
        admin_engine.dispose()


def test_account_identity_migration_round_trip(migration_database):
    engine, env = migration_database

    def migrate(command, revision):
        subprocess.run(
            [sys.executable, "-m", "alembic", command, revision],
            cwd=BACKEND_DIR,
            env=env,
            check=True,
        )

    migrate("upgrade", LEGACY_REVISION)
    insert_user = text("INSERT INTO users (username) VALUES (:username)")
    usernames = ["AnotherCook", "VoHiYo"]
    with engine.begin() as connection:
        connection.execute(insert_user, [{"username": name} for name in usernames])

    migrate("upgrade", "head")
    with engine.connect() as connection:
        users = connection.execute(text("SELECT username, auth_id FROM users ORDER BY id")).all()
    assert [user.username for user in users] == usernames
    auth_ids = {user.auth_id for user in users}
    assert len(auth_ids) == len(usernames)
    assert all(len(auth_id) == 32 for auth_id in auth_ids)
    assert inspect(engine).has_table("refresh_sessions")
    with pytest.raises(IntegrityError), engine.begin() as connection:
        connection.execute(
            text("INSERT INTO users (username, auth_id) VALUES (:username, :auth_id)"),
            {"username": "vohiyo", "auth_id": uuid4().hex},
        )

    migrate("downgrade", LEGACY_REVISION)
    assert not inspect(engine).has_table("refresh_sessions")
    assert "auth_id" not in {column["name"] for column in inspect(engine).get_columns("users")}
    with engine.connect() as connection:
        assert connection.scalars(text("SELECT username FROM users ORDER BY id")).all() == usernames
