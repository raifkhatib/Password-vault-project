import os
import secrets
from datetime import timedelta
from pathlib import Path

from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    session,
    url_for
)
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user
)
from flask_session import Session as ServerSession
from flask_wtf.csrf import CSRFProtect

from forms import (
    CredentialForm,
    LoginForm,
    PasswordGeneratorForm,
    RegistrationForm
)
from models import Credential, User, db
from security import (
    decrypt_text,
    derive_vault_key,
    encrypt_text,
    generate_secure_password
)


app = Flask(__name__)

session_directory = Path(app.instance_path) / "sessions"
session_directory.mkdir(parents=True, exist_ok=True)

app.config["SECRET_KEY"] = (
    os.environ.get("SECRET_KEY") or secrets.token_hex(32)
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vault.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = str(session_directory)
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

db.init_app(app)
csrf = CSRFProtect(app)
server_session = ServerSession(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access your vault."


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def get_vault_key():
    stored_key = session.get("vault_key")

    if stored_key is None:
        return None

    return stored_key.encode("utf-8")


def require_vault_key():
    vault_key = get_vault_key()

    if vault_key is None:
        logout_user()
        session.clear()
        flash("Your vault session expired. Please log in again.")

    return vault_key


def get_owned_credential(credential_id):
    credential = db.session.scalar(
        db.select(Credential).where(
            Credential.id == credential_id,
            Credential.user_id == current_user.id
        )
    )

    if credential is None:
        abort(404)

    return credential


def credential_for_display(credential, vault_key):
    return {
        "id": credential.id,
        "service": decrypt_text(
            vault_key,
            credential.service_encrypted
        ),
        "login_username": decrypt_text(
            vault_key,
            credential.username_encrypted
        ),
        "password": decrypt_text(
            vault_key,
            credential.password_encrypted
        ),
        "website": decrypt_text(
            vault_key,
            credential.website_encrypted
        ),
        "notes": decrypt_text(
            vault_key,
            credential.notes_encrypted
        ),
        "created_at": credential.created_at,
        "updated_at": credential.updated_at
    }


def encrypt_credential_form(credential, form, vault_key):
    credential.service_encrypted = encrypt_text(
        vault_key,
        form.service.data.strip()
    )
    credential.username_encrypted = encrypt_text(
        vault_key,
        form.login_username.data.strip()
    )
    credential.password_encrypted = encrypt_text(
        vault_key,
        form.password.data
    )
    credential.website_encrypted = encrypt_text(
        vault_key,
        form.website.data.strip() if form.website.data else ""
    )
    credential.notes_encrypted = encrypt_text(
        vault_key,
        form.notes.data.strip() if form.notes.data else ""
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("vault"))

    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data.strip().lower()

        existing_user = db.session.scalar(
            db.select(User).where(User.username == username)
        )

        if existing_user:
            form.username.errors.append(
                "That username is already registered."
            )
        else:
            user = User(username=username)
            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()

            flash("Account created. You can now log in.")
            return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("vault"))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data.strip().lower()

        user = db.session.scalar(
            db.select(User).where(User.username == username)
        )

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or master password.")
        else:
            vault_key = derive_vault_key(
                form.password.data,
                user.encryption_salt
            )

            session.clear()
            login_user(user)
            session.permanent = True
            session["vault_key"] = vault_key.decode("utf-8")

            flash("Login successful.")
            return redirect(url_for("vault"))

    return render_template("login.html", form=form)


@app.route("/vault")
@login_required
def vault():
    vault_key = require_vault_key()

    if vault_key is None:
        return redirect(url_for("login"))

    credential_records = db.session.scalars(
        db.select(Credential)
        .where(Credential.user_id == current_user.id)
        .order_by(Credential.updated_at.desc())
    ).all()

    credentials = [
        credential_for_display(record, vault_key)
        for record in credential_records
    ]

    return render_template(
        "vault.html",
        credentials=credentials
    )


@app.route("/vault/add", methods=["GET", "POST"])
@login_required
def add_credential():
    vault_key = require_vault_key()

    if vault_key is None:
        return redirect(url_for("login"))

    form = CredentialForm()

    if form.validate_on_submit():
        credential = Credential(user_id=current_user.id)
        encrypt_credential_form(credential, form, vault_key)

        db.session.add(credential)
        db.session.commit()

        flash("Credential encrypted and saved.")
        return redirect(url_for("vault"))

    return render_template(
        "credential_form.html",
        form=form,
        page_title="Add credential"
    )


@app.route("/vault/<int:credential_id>")
@login_required
def view_credential(credential_id):
    vault_key = require_vault_key()

    if vault_key is None:
        return redirect(url_for("login"))

    credential = get_owned_credential(credential_id)
    displayed_credential = credential_for_display(
        credential,
        vault_key
    )

    return render_template(
        "credential_detail.html",
        credential=displayed_credential
    )


@app.route("/vault/<int:credential_id>/edit", methods=["GET", "POST"])
@login_required
def edit_credential(credential_id):
    vault_key = require_vault_key()

    if vault_key is None:
        return redirect(url_for("login"))

    credential = get_owned_credential(credential_id)
    displayed_credential = credential_for_display(
        credential,
        vault_key
    )

    form = CredentialForm(data=displayed_credential)

    if form.validate_on_submit():
        encrypt_credential_form(credential, form, vault_key)
        db.session.commit()

        flash("Credential updated and encrypted.")
        return redirect(
            url_for(
                "view_credential",
                credential_id=credential.id
            )
        )

    return render_template(
        "credential_form.html",
        form=form,
        page_title="Edit credential"
    )


@app.route("/vault/<int:credential_id>/delete", methods=["POST"])
@login_required
def delete_credential(credential_id):
    vault_key = require_vault_key()

    if vault_key is None:
        return redirect(url_for("login"))

    credential = get_owned_credential(credential_id)

    db.session.delete(credential)
    db.session.commit()

    flash("Credential deleted.")
    return redirect(url_for("vault"))


@app.route("/generator", methods=["GET", "POST"])
@login_required
def password_generator():
    form = PasswordGeneratorForm()
    generated_password = None

    if form.validate_on_submit():
        generated_password = generate_secure_password(
            form.length.data
        )

    return render_template(
        "generator.html",
        form=form,
        generated_password=generated_password
    )


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("home"))


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)