from flask_login import current_user, UserMixin as _UserMixin
from sqlorm import SQL, execute, Column, Relationship
from flask_sqlorm import Model
from werkzeug.local import LocalProxy
from hyperflask import current_app, abort
from hyperflask.utils.tokens import create_token, load_token
from .passlib import hash_password, verify_password
import abc
import datetime


class MissingUserModelError(Exception):
    pass


def get_user_model():
    for model in current_app.db.Model.__model_registry__.values():
        if issubclass(model, UserMixin):
            return model
    raise MissingUserModelError()


UserModel = LocalProxy(get_user_model)


class UserMixin(_UserMixin, Model, abc.ABC):
    __mercure_payload_attrs__ = ('id', 'display_name')

    email = Column(type=str)
    password = Column(type=str)
    email_validated = Column(type=bool, default=False)
    email_validated_at = Column(type=datetime.datetime)
    signup_at = Column(type=datetime.datetime, default=datetime.datetime.utcnow)
    signup_from = Column(type=str)
    signup_using = Column(type=str)
    last_login_at = Column(type=datetime.datetime)
    last_login_from = Column(type=str)
    last_login_using = Column(type=str)

    @classmethod
    def from_token(cls, token, **serializer_kwargs):
        user_id = load_token(token, **serializer_kwargs)
        if user_id:
            return cls.get(user_id)

    @classmethod
    def from_token_or_404(cls, token, **serializer_kwargs):
        user = cls.from_token(token, **serializer_kwargs)
        if not user:
            abort(404)
        return user

    @property
    def display_name(self):
        return self.email

    @execute
    def update_password(self, password):
        self.password = hash_password(password)
        return SQL.update(self.table, {"password": self.password}).where(self.__mapper__.primary_key_condition(self))

    def verify_password(self, password):
        return verify_password(password, self.password)

    def create_token(self, **serializer_kwargs):
        return create_token(self.__mapper__.get_primary_key(self), **serializer_kwargs)

    def validate_email(self):
        self.email_validated = True
        self.email_validated_at = datetime.datetime.utcnow()


class UserRelatedMixin(Model, abc.ABC):
    user_id: int
    user = Relationship(UserModel, source_col="user_id", single=True)

    @classmethod
    def find_all_for_current_user(cls, *args, **kwargs):
        return cls.find_all(*args, user_id=current_user.id, **kwargs)

    @classmethod
    def find_one_for_current_user(cls, *args, **kwargs):
        return cls.find_one(*args, user_id=current_user.id, **kwargs)

    @classmethod
    def find_one_for_current_user_or_404(cls, *args, **kwargs):
        return cls.find_one_or_404(*args, user_id=current_user.id, **kwargs)

    @classmethod
    def get_for_current_user(cls, pk, **kwargs):
        return cls.find_one(cls.__mapper__.primary_key_condition(pk), user_id=current_user.id, **kwargs)

    @classmethod
    def get_for_current_user_or_404(cls, pk, **kwargs):
        obj = cls.get_for_current_user(pk, **kwargs)
        if not obj:
            abort(404)
        return obj

    @classmethod
    def create_for_current_user(cls, **kwargs):
        return cls.create(user=current_user, **kwargs)

