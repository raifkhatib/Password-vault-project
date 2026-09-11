import pytest
from flask import Flask

from models import Credential, User, db


@pytest.fixture()
def database_app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_password_is_hashed_and_verified(database_app):
    with database_app.app_context():
        user = User(username="modeltest")
        user.set_password("TemporaryMasterPassword!")

        assert user.password_hash != "TemporaryMasterPassword!"
        assert user.check_password("TemporaryMasterPassword!")
        assert not user.check_password("WrongPassword!")


def test_user_receives_random_encryption_salt(database_app):
    with database_app.app_context():
        user = User(username="salttest")
        user.set_password("TemporaryMasterPassword!")

        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert len(user.encryption_salt) == 16


def test_credential_is_linked_to_its_owner(database_app):
    with database_app.app_context():
        user = User(username="ownertest")
        user.set_password("TemporaryMasterPassword!")

        db.session.add(user)
        db.session.commit()

        credential = Credential(
            user_id=user.id,
            service_encrypted="encrypted-service",
            username_encrypted="encrypted-username",
            password_encrypted="encrypted-password",
            website_encrypted="encrypted-website",
            notes_encrypted="encrypted-notes"
        )

        db.session.add(credential)
        db.session.commit()

        saved_credential = db.session.scalar(
            db.select(Credential).where(
                Credential.user_id == user.id
            )
        )

        assert saved_credential is not None
        assert saved_credential.owner.id == user.id