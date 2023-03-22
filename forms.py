from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, URL, EqualTo, ValidationError
from flask import session, g
from models import User


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField(
        'Username',
        validators=[DataRequired()],
    )

    email = StringField(
        'E-mail',
        validators=[DataRequired(), Email()],
    )

    password = PasswordField(
        'Password',
        validators=[Length(min=6)],
    )

    image_url = StringField(
        '(Optional) Image URL',
        validators=[URL()]
    )


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField(
        'Username',
        validators=[DataRequired()],
    )

    password = PasswordField(
        'Password',
        validators=[Length(min=6)],
    )

class CsrfForm(FlaskForm):
    """For actions where we want CSRF protection, but don't need any fields.

    Currently used for our "delete" buttons, which make POST requests, and the
    logout button, which makes POST requests.
    """

class EditUserProfile(FlaskForm):
    """Edit User Form"""

    username = StringField(
        'Username',
        validators=[DataRequired()],
    )

    email = StringField(
        'E-mail',
        validators=[DataRequired(), Email()],
    )

    password = PasswordField(
        'Password',
        validators=[Length(min=6)],
    )

    # password = PasswordField('New Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')])
    # confirm  = PasswordField('Repeat Password')

    image_url = StringField(
        '(Optional) Image URL',
        validators=[URL()]
    )

    header_image_url = StringField(
        '(Optional) URL or JPEG',
    )

    bio = StringField(
        '(Optional) Bio'
    )

    # def validate_password(self, password):
    #     user = User.query.filter_by(username = self.username.data)

    #     if not user.check_password(password):
    #         return False





