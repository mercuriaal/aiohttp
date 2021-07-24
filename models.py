from datetime import date
import hashlib

from aiohttp import web
from asyncpg import UniqueViolationError
from gino import Gino


db = Gino()


class BaseModel:

    @classmethod
    async def get_or_404(cls, id):
        instance = await cls.get(id)
        if instance:
            return instance
        raise web.HTTPNotFound()

    @classmethod
    async def create_instance(cls, **kwargs):
        try:
            instance = await cls.create(**kwargs)
        except UniqueViolationError:
            raise web.HTTPBadRequest()
        return instance


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))

    def __str__(self):
        return f'<User {self.username}>'

    def __repr__(self):
        return str(self)

    def set_password(self, raw_password: str):
        self.password = hashlib.md5(raw_password.encode()).hexdigest()

    def check_password(self, raw_password: str):
        return self.password == hashlib.md5(raw_password.encode()).hexdigest()


class Advertisement(db.Model, BaseModel):
    __tablename__ = 'advertisement'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(256))
    created_at = db.Column(db.Date, default=date.today())
    owner = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description
        }
