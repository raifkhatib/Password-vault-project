import os
import secrets
from datetime import timedelta

from flask import Flask, flash, redirect, render_template, session, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user
)
from flask_wtf.csrf import CSRFProtect

from forms import LoginForm, RegistrationForm
from models import User, db


app = Flask(__name__)

app.config["SECRET_KEY"] = (
    os.environ.get("SECRET_KEY") or secrets.token_hex(32)
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vault.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access your vault."


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


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
            form.username.errors.append("That username is already registered.")
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
            session.clear()
            login_user(user)
            session.permanent = True

            flash("Login successful.")
            return redirect(url_for("vault"))

    return render_template("login.html", form=form)


@app.route("/vault")
@login_required
def vault():
    return render_template("vault.html")


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