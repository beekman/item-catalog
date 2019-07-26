#!/usr/bin/env python3
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from marshmallow import Schema, fields
from flask_marshmallow import Marshmallow
from flask import Flask

app = Flask(__name__)
ma = Marshmallow(app)
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    password_hash = Column(String(64))
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


def hash_password(self, password):
    self.password_hash = pwd_context.encrypt(password)


def verify_password(self, password):
    return pwd_context.verify(password, self.password_hash)


def generate_auth_token(self, expiration=600):
    s = Serializer(secret_key, expires_in=expiration)
    return s.dumps({'id': self.id})


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    slug = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'name': self.name,
            'id': self.id
        }

    def __repr__(self):
        return "<Category(Category:'%s')>" % (self.category_name)


class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    slug = Column(String(80), nullable=False)
    description = Column(String(1000))
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }

    def __repr__(self):
        return "<Item(id='%s', name='%s', slug='%s')>" % (
            self.id, self.name, self.slug)


class ItemSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'description')


class CategorySchema(ma.Schema):
    fields = ('id', 'name')


# categorytree = fields.Nested(ItemSchema)
categories_schema = CategorySchema(many=True)

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
