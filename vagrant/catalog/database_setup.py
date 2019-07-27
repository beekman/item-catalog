#!/usr/bin/env python3
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from flask import Flask
from passlib.apps import custom_app_context as pwd_context
import random
import string
from itsdangerous import(TimedJSONWebSignatureSerializer
                         as Serializer,
                         BadSignature,
                         SignatureExpired)

app = Flask(__name__)
Base = declarative_base()

secret_key = ''.join(random.choice(
    string.ascii_uppercase + string.digits) for x in range(32))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(40), index=True)
    name = Column(String(250))
    password_hash = Column(String(64))
    email = Column(String(250))
    picture = Column(String(250))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # Valid but Expired token
            return None
        except BadSignature:
            # Token is Invalid
            return None
        user_id = data['id']
        return user_id
# @staticmethod


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


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
