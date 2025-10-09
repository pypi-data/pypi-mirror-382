from flask_login import current_user, LoginManager, login_required
from flask_file_routes import DEFAULT_HELPERS, decorator_as_page_helper, ModuleView
from sqlorm.sql_template import SQLTemplate
from jinja2 import FileSystemLoader
from hyperflask import lazy_gettext
from .model import UserMixin, UserModel, UserRelatedMixin, MissingUserModelError
from .blueprint import users_blueprint
from .jinja_ext import LoginRequiredExtension, AnonymousOnlyExtension
from .flow import signup, login, logout, validate_password, send_reset_password_email, reset_password
from .signals import *
from dataclasses import dataclass
import typing as t
import os


@dataclass
class UsersState:
    signup_default_redirect_url: str
    reset_password_redirect_url: str
    login_redirect_url: str
    logout_redirect_url: str
    token_max_age: int
    allowed_flows: t.Sequence[str]
    forgot_password_flash_message: t.Optional[str]
    signup_email_template: t.Optional[str]
    reset_password_email_template: t.Optional[str]


class Users:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app, register_blueprint=True):
        state = app.extensions['users'] = UsersState(
            signup_default_redirect_url=app.config.get('USERS_SIGNUP_DEFAULT_REDIRECT_URL', '/'),
            signup_email_template=app.config.get('USERS_SIGNUP_EMAIL_TEMPLATE'),
            login_redirect_url=app.config.get('USERS_LOGIN_REDIRECT_URL', '/'),
            forgot_password_flash_message=app.config.get('USERS_FORGOT_PASSWORD_FLASH_MESSAGE', lazy_gettext("An email has been sent with instructions on how to reset your password")),
            reset_password_email_template=app.config.get('USERS_RESET_PASSWORD_EMAIL_TEMPLATE'),
            reset_password_redirect_url=app.config.get('USERS_RESET_PASSWORD_REDIRECT_URL', '/'),
            logout_redirect_url=app.config.get('USERS_LOGOUT_REDIRECT_URL', '/'),
            token_max_age=app.config.get('USERS_TOKEN_MAX_AGE', 3600),
            allowed_flows=app.config.get('USERS_ALLOWED_FLOWS', ['connect']),
        )

        manager = LoginManager(app)
        manager.login_view = 'users.connect' if 'connect' in state.allowed_flows else 'users.login'

        if register_blueprint:
            app.register_blueprint(users_blueprint)

        @manager.user_loader
        def load_user(user_id):
            try:
                return UserModel.get(user_id)
            except MissingUserModelError:
                return

        DEFAULT_HELPERS.update(login_required=decorator_as_page_helper(login_required))
        ModuleView.module_globals.update(current_user=current_user)
        SQLTemplate.eval_globals.update(current_user=current_user)
        app.jinja_env.globals.update(current_user=current_user)
        app.jinja_env.add_extension(LoginRequiredExtension)
        app.jinja_env.add_extension(AnonymousOnlyExtension)
        app.macros.register_from_file(os.path.join(os.path.dirname(__file__), "macros.html"))
        app.assets.state.tailwind_sources.append(os.path.join(os.path.dirname(__file__), "templates"))
        app.extensions['mail_templates'].loaders.append(FileSystemLoader(os.path.join(os.path.dirname(__file__), 'emails')))
        if app.config.get('RECAPTCHA_SITE_KEY'):
            app.config['CSP_SAFE_URLS'].append('https://www.google.com/recaptcha/api.js')
            app.config['CSP_SAFE_URLS'].append('https://www.gstatic.com')

        @app.sse.payload_getter
        def get_sse_payload(topics):
            if current_user.is_authenticated:
                return {'user': {k: getattr(current_user, k, None) for k in current_user.__mercure_payload_attrs__}}
            return {}
