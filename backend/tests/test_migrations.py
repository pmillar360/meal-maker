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

    with engine.begin() as connection:
        connection.execute(text("INSERT INTO recipes (id, title, spoonacular_id, last_updated, is_featured) VALUES (42, 'Soup', 12, CURRENT_TIMESTAMP, false)"))
        connection.execute(text("INSERT INTO ingredients (id, name, spoonacular_id) VALUES (20, 'Scallions', 31), (10, 'Salt', 15)"))
        connection.execute(text("INSERT INTO recipe_ingredient (recipe_id, ingredient_id, quantity) VALUES (42, 20, '2'), (42, 10, '1')"))
        connection.execute(text("INSERT INTO favourite_recipes (user_id, recipe_id) SELECT id, 42 FROM users"))

    migrate("upgrade", "head")
    with engine.connect() as connection:
        assert connection.execute(text("SELECT provider, external_id FROM recipes WHERE id=42")).one() == ("spoonacular", "12")
        assert connection.execute(text("SELECT ingredient_id, quantity FROM recipe_ingredient ORDER BY position")).all() == [(10, "1"), (20, "2")]
        assert connection.scalar(text("SELECT lookup_key FROM ingredients WHERE id=20")) == "green onion"
        assert connection.scalar(text("SELECT COUNT(*) FROM favourite_recipes WHERE recipe_id=42")) == 2
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

    with engine.begin() as connection:
        connection.execute(text("INSERT INTO ingredients (id, name, lookup_key) VALUES (30, 'Water', 'water')"))
        connection.execute(text("INSERT INTO ingredient_sources VALUES ('spoonacular', '50', 30), ('spoonacular', '51', 30)"))
    with pytest.raises(subprocess.CalledProcessError):
        migrate("downgrade", LEGACY_REVISION)
    with engine.begin() as connection:
        assert connection.scalar(text("SELECT COUNT(*) FROM ingredient_sources WHERE ingredient_id=30")) == 2
        connection.execute(text("DELETE FROM ingredient_sources WHERE external_id='51'"))
    migrate("downgrade", LEGACY_REVISION)
    assert not inspect(engine).has_table("refresh_sessions")
    assert "auth_id" not in {column["name"] for column in inspect(engine).get_columns("users")}
    with engine.connect() as connection:
        assert connection.scalars(text("SELECT username FROM users ORDER BY id")).all() == usernames
        assert connection.scalar(text("SELECT spoonacular_id FROM ingredients WHERE id=30")) == 50


def test_concurrent_imports_share_identity(migration_database):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from sqlalchemy.orm import Session
    from app.models import Base, Recipe, RecipeIngredient
    from crud.recipe_import import save_import
    from tests.normalization_fixtures import fixture_recipes

    engine, _ = migration_database
    Base.metadata.create_all(engine)
    barrier = Barrier(2)
    def run():
        with Session(engine) as db:
            barrier.wait(timeout=10)
            return save_import(db, fixture_recipes()[0]).id

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(run) for _ in range(2)]
        assert futures[0].result(timeout=20) == futures[1].result(timeout=20)
    with Session(engine) as db:
        assert db.query(Recipe).count() == 1
        assert db.query(RecipeIngredient).count() == 3
