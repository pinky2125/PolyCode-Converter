from pathlib import Path
import os
import sqlite3

from app import app
import database


def test_home_post_without_required_fields_does_not_crash():
    app.config["TESTING"] = True
    with app.test_client() as client:
        response = client.post("/", data={})
    assert response.status_code == 200


def test_database_uses_project_relative_path(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    import importlib

    importlib.reload(database)
    conn = database.connect_db()
    try:
        db_path = Path(conn.execute("PRAGMA database_list").fetchone()[2]).resolve()
    finally:
        conn.close()

    assert db_path == (Path(database.__file__).resolve().parent / "database.db").resolve()


def test_home_page_includes_browser_script():
    app.config["TESTING"] = True
    with app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "static/script.js" in html
