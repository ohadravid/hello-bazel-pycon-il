import pytest
from pathlib import Path
import demo.bazel_app as bazel_app


@pytest.fixture()
def app():
    app = bazel_app.app
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


def test_request_example(client):
    response = client.get("/")
    assert b"<p>Hello, World!</p>" in response.data


DOG = Path(__file__).parent / "dog.jpg"


def test_dog_example(client):
    response = client.post(
        "/classify", data=DOG.read_bytes(), content_type="application/octet-stream"
    ).json
    assert response["result"].lower() == "samoyed", f"Expected a dog, got {response}"
