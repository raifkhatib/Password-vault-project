from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    IntegerField,
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField
)
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Length,
    NumberRange,
    Optional,
    Regexp,
    URL
)


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


class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=30)
        ]
    )

    password = PasswordField(
        "Master password",
        validators=[
            DataRequired(),
            Length(min=1, max=128)
        ]
    )

    submit = SubmitField("Log in")


class CredentialForm(FlaskForm):
    service = StringField(
        "Service name",
        validators=[
            DataRequired(),
            Length(max=120)
        ]
    )

    login_username = StringField(
        "Username or email",
        validators=[
            DataRequired(),
            Length(max=180)
        ]
    )

    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(max=256)
        ]
    )

    website = StringField(
        "Website",
        validators=[
            Optional(),
            URL(),
            Length(max=255)
        ]
    )

    notes = TextAreaField(
        "Private notes",
        validators=[
            Optional(),
            Length(max=1000)
        ]
    )

    submit = SubmitField("Save credential")


class PasswordGeneratorForm(FlaskForm):
    length = IntegerField(
        "Password length",
        default=20,
        validators=[
            DataRequired(),
            NumberRange(min=12, max=128)
        ]
    )

    submit = SubmitField("Generate password")