from flask_login import login_user, logout_user
from hyperflask import send_mail, current_app
import random
import datetime
from . import signals
from .passlib import hash_password
from .model import UserModel


class UserFlowError(Exception):
    pass


def signup(data=None, **kwargs):
    data = dict(data) if data else {}
    data.update(kwargs)

    if "password" in data:
        if not validate_password(data['password']):
            raise UserFlowError()
        data['password'] = hash_password(data['password'])

    signals.user_before_signup.send(current_app, data=data)
    with current_app.db:
        user = UserModel.create(**data)
    current_app.logger.info(f"[AUTH] New signup for user #{user.id}")
    signals.user_signed_up.send(current_app, user=user)
    login(user)
    email_template = current_app.extensions['users'].signup_email_template
    if email_template:
        send_mail(email_template, user.email, user=user)
    return user


def login(user, password=None, remember=False, login_using=None, validate_email=False):
    if password and not user.verify_password(password):
        raise UserFlowError()
    login_user(user, remember=remember)
    current_app.logger.info(f"[AUTH] User #{user.id} logged in")
    with current_app.db:
        if validate_email and not user.email_validated:
            user.validate_email()
        user.last_login_at = datetime.datetime.utcnow()
        user.last_login_using = login_using
        user.save()


def send_login_link(user):
    token = user.create_token()
    code = str(random.randrange(100000, 999999))
    send_mail("users/login_link.mjml", user.email, token=token, code=code)
    current_app.logger.debug(f"[AUTH] Login link with code {code} email sent to {user.email}")
    return code


def logout():
    logout_user()


def validate_password(password):
    return True


def send_reset_password_email(user):
    token = user.create_token()
    send_mail("users/forgot_password.mjml", user.email, token=token)
    current_app.logger.info(f"[AUTH] Password reset email sent to user #{user.id}")
    return token


def reset_password(user, password):
    if not validate_password(password):
        raise UserFlowError()
    with current_app.db:
        user.update_password(password)
    current_app.logger.info(f"[AUTH] Password reset for user #{user.id}")
    login(user)
    email_template = current_app.extensions['users'].reset_password_email_template
    if email_template:
        send_mail(email_template, user.email, user=user)
