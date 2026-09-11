import pytest

from app import app


@pytest.fixture()
def client():
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_security_headers_are_present(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "no-referrer"
    assert response.headers["Cross-Origin-Opener-Policy"] == "same-origin"
    assert "default-src 'self'" in response.headers[
        "Content-Security-Policy"
    ]


def test_vault_requires_authentication(client):
    response = client.get("/vault")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
    assert "no-store" in response.headers["Cache-Control"]


def test_registration_rejects_missing_csrf_token(client):
    response = client.post(
        "/register",
        data={
            "username": "csrfcheck",
            "password": "TemporaryMasterPassword!",
            "confirm_password": "TemporaryMasterPassword!"
        }
    )

    assert response.status_code == 400