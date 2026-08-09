import pytest
from werkzeug.security import generate_password_hash

from learning_inbox import create_app
from learning_inbox.extensions import db
from learning_inbox.models import User


@pytest.fixture()
def app(tmp_path):
    database_path = (tmp_path / "test.db").as_posix()

    class TestConfig:
        TESTING = True
        SECRET_KEY = "test-secret-key"
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{database_path}"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        WTF_CSRF_ENABLED = False

    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.engine.dispose()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def users(app):
    with app.app_context():
        first_user = User(
            login_id="user1",
            password_hash=generate_password_hash("password123"),
        )
        second_user = User(
            login_id="user2",
            password_hash=generate_password_hash("password123"),
        )
        db.session.add_all([first_user, second_user])
        db.session.commit()
        return {"first_id": first_user.id, "second_id": second_user.id}


@pytest.fixture()
def logged_in_client(client, users):
    response = client.post(
        "/auth/login",
        data={"login_id": "user1", "password": "password123"},
    )
    assert response.status_code == 302
    return client
