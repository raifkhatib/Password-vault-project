import os
import secrets

from flask import Flask, flash, redirect, render_template, url_for

from forms import RegistrationForm
from models import User, db


app = Flask(__name__)

app.config["SECRET_KEY"] = (
    os.environ.get("SECRET_KEY") or secrets.token_hex(32)
)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///vault.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
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

            flash("Account created successfully.")
            return redirect(url_for("home"))

    return render_template("register.html", form=form)


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)