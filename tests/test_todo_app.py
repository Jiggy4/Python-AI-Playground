from pathlib import Path

import pytest

from app import app

DATA_FILE = Path(__file__).resolve().parents[1] / "tasks.json"


@pytest.fixture(autouse=True)
def reset_task_store():
    if DATA_FILE.exists():
        DATA_FILE.unlink()
    yield
    if DATA_FILE.exists():
        DATA_FILE.unlink()


def test_todo_list_adds_task():
    with app.test_client() as client:
        response = client.post(
            "/",
            data={"action": "add", "title": "Write project proposal", "due_date": "2026-09-30"},
            follow_redirects=True,
        )

        assert response.status_code == 200
        assert b"Write project proposal" in response.data
        assert b"2026-09-30" in response.data


def test_todo_list_can_mark_done_and_delete():
    with app.test_client() as client:
        client.post(
            "/",
            data={"action": "add", "title": "Plan sprint review", "due_date": "2026-10-01"},
            follow_redirects=True,
        )

        response = client.post(
            "/",
            data={"action": "toggle", "task_id": "0"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"completed" in response.data.lower()

        response = client.post(
            "/",
            data={"action": "delete", "task_id": "0"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Plan sprint review" not in response.data
