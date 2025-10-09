from flask import current_app
from werkzeug.local import LocalProxy
from passlib.context import CryptContext


def get_crypt_context():
    if not hasattr(current_app, "crypt_context"):
        current_app.crypt_context = CryptContext(schemes=current_app.config.get("PASSLIB_CRYPT_CONTEXT_SCHEMES", ["bcrypt"]))
    return current_app.crypt_context


crypt_context = LocalProxy(get_crypt_context)


def hash_password(password):
    return crypt_context.hash(password)


def verify_password(password, hash):
    return crypt_context.verify(password, hash)