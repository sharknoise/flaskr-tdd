import json
import pytest
from pathlib import Path

from project.app import app, db

TEST_DB = "test.db"


@pytest.fixture
def client():
    """Set up a state for each test function before running."""
    BASE_DIR = Path(__file__).resolve().parent.parent
    app.config["TESTING"] = True
    app.config["DATABASE"] = BASE_DIR.joinpath(TEST_DB)
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"sqlite:///{BASE_DIR.joinpath(TEST_DB)}"

    db.create_all()  # setup
    yield app.test_client()  # tests run here
    db.drop_all()  # teardown


def login(client, username, password):
    """Log in (helper function)."""
    return client.post(
        "/login",
        data=dict(username=username, password=password),
        follow_redirects=True,
    )


def logout(client):
    """Log out (helper function)."""
    return client.get("/logout", follow_redirects=True)


def test_index(client):
    """Ensure the homepage response is OK."""
    response = client.get("/", content_type="html/text")
    assert response.status_code == 200


def test_database():
    """Ensure that the test database exists."""
    tester = Path(TEST_DB).is_file()
    assert tester


def test_empty_db(client):
    """Ensure the database is blank."""
    rv = client.get("/")
    assert b"No entries yet. Add some!" in rv.data


def test_login_logout(client):
    """Test login and logout using helper functions."""
    rv = login(client, app.config["USERNAME"], app.config["PASSWORD"])
    assert b"You were logged in" in rv.data
    rv = logout(client)
    assert b"You were logged out" in rv.data
    rv = login(client, app.config["USERNAME"] + "x", app.config["PASSWORD"])
    assert b"Invalid username" in rv.data
    rv = login(client, app.config["USERNAME"], app.config["PASSWORD"] + "x")
    assert b"Invalid password" in rv.data


def test_messages(client):
    """Ensure that user can post messages."""
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    rv = client.post(
        "/add",
        data=dict(title="<Hello>", text="<strong>HTML</strong> allowed here"),
        follow_redirects=True,
    )
    assert b"No entries here so far" not in rv.data
    assert b"&lt;Hello&gt;" in rv.data
    assert b"<strong>HTML</strong> allowed here" in rv.data


def test_delete_message(client):
    """Ensure the messages are being deleted."""
    rv = client.get("/delete/1")
    data = json.loads(rv.data)
    assert data["status"] == 0
    login(client, app.config["USERNAME"], app.config["PASSWORD"])
    rv = client.get("/delete/1")
    data = json.loads(rv.data)
    assert data["status"] == 1


def test_search(client):
    """Ensure that the search shows expected entries."""
    rv = login(client, app.config["USERNAME"], app.config["PASSWORD"])
    rv = client.post(
        "/add",
        data=dict(title="Good title 1", text="Text 1"),
    )
    rv = client.post(
        "/add",
        data=dict(title="Title 2", text="Good text 2"),
    )
    rv = client.post(
        "/add",
        data=dict(title="Bad title", text="Bad text"),
    )
    rv = client.get("/search/?query=good")
    assert b"Good title 1" in rv.data
    assert b"Good text 2" in rv.data
    assert b"Bad title" not in rv.data
