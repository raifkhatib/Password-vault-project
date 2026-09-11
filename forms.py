from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, Regexp


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=30),
            Regexp(
                r"^[A-Za-z0-9_]+$",
                message="Use only letters, numbers, and underscores."
            )
        ]
    )

    password = PasswordField(
        "Master password",
        validators=[
            DataRequired(),
            Length(min=12, max=128)
        ]
    )

    confirm_password = PasswordField(
        "Confirm master password",
        validators=[
            DataRequired(),
            EqualTo("password", message="The passwords must match.")
        ]
    )

    submit = SubmitField("Create account")