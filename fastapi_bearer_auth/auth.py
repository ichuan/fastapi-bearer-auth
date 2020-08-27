#!/usr/bin/env python
# coding: utf-8
# yc@2020/08/27

from datetime import datetime, timedelta

import jwt
from jwt import PyJWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from . import config


# TODO: tokenUrl
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/user/signin')


async def create_access_token(user, expires: timedelta = None):
    if expires is None:
        expires = timedelta(minutes=config.get('ACCESS_TOKEN_EXPIRE_MINUTES'))
    data = {
        'sub': getattr(user, 'username', None) or user['username'],
        'exp': datetime.utcnow() + expires,
    }
    return jwt.encode(data, config.get('SECRET_KEY'), algorithm=config.get('ALGORITHM'))


async def decode_access_token(token: str):
    try:
        data = jwt.decode(
            token, config.get('SECRET_KEY'), algorithm=config.get('ALGORITHM')
        )
        return await config.call('get_user_by_name', data.get('sub'))
    except PyJWTError:
        pass


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = await decode_access_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail='Invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return user
