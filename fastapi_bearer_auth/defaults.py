#!/usr/bin/env python
# coding: utf-8
# yc@2020/08/27

"""
You should implement at least get_user_by_name() and create_user()
"""

import os

from passlib.context import CryptContext

from . import config

user_store = {}
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
consts = {
    'ACCESS_TOKEN_EXPIRE_MINUTES': int(
        os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 60 * 24 * 365)
    ),
    'ALGORITHM': 'HS256',
    'SECRET_KEY': os.getenv('SECRET_KEY', os.urandom(32).hex()),
    # user object field name for jwt sub
    'USER_FIELD_FOR_JWT_SUB': 'username',
}


async def get_user_by_name(username, **extra_fields):
    """
    return a User object or None
    """
    return user_store.get(username)


async def create_user(
    username,
    password,
    username_field='username',
    **extra_fields,
):
    """
    user signups, create a user in backend db
    return a User object
    """
    if await config.call('get_user_by_name', username, **extra_fields):
        raise ValueError('User {} exists'.format(username))
    user = {
        username_field: username,
        'password': await config.call('get_password_hash', password),
        **extra_fields,
    }
    user_store[username] = user
    return user


async def authenticate(username, password, **extra_fields):
    """
    return a User object or None
    """
    user = await config.call('get_user_by_name', username, **extra_fields)
    if user:
        hashed_password = getattr(user, 'password', None) or user['password']
        if await config.call('verify_password', password, hashed_password):
            return user


async def verify_password(plain_password, hashed_password):
    """
    returns True or False
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


async def get_password_hash(password):
    return pwd_context.hash(password)
