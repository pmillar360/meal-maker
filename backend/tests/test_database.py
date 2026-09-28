import os
import subprocess
import sys
from pathlib import Path


def test_plain_postgresql_url_uses_installed_driver():
    env = os.environ.copy()
    env["DATABASE_URL"] = "postgresql://user:password@localhost/testdb"

    result = subprocess.run(
        [sys.executable, "-c", "from app.database import engine; print(engine.dialect.driver)"],
        cwd=Path(__file__).resolve().parents[1],
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "psycopg2"
