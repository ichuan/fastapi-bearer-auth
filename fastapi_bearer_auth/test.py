#!/usr/bin/env python
# coding: utf-8
# yc@2020/08/27

from fastapi import Depends, FastAPI
from pydantic import BaseModel

import fastapi_bearer_auth as fba


class UserOut(BaseModel):
    username: str


app = FastAPI(title='Test App')
# simple in-memory db
users = {}


# Two required handler: handle_get_user_by_name and handle_create_user
@fba.handle_get_user_by_name  # type: ignore
async def get_user_by_name(name, **extra_fields):
    return users.get(name)


@fba.handle_create_user  # type: ignore
async def create_user(username, password, **extra_fields):
    if await get_user_by_name(username):
        raise ValueError('User {} exists'.format(username))
    user = {
        'username': username,
        'password': await fba.call_config('get_password_hash', password),
        **extra_fields,
    }
    users[username] = user
    return user


# Three router depends available: fba.signup, fba.signin and fba.get_current_user
# fba.signup resolve to User object
@app.post('/user/signup', response_model=UserOut)
async def signup(user=Depends(fba.signup)):
    return user


# fba.signin resolve to {user: <user_object>, token: {token_type, access_token}}
@app.post('/user/signin')
async def signin(ret=Depends(fba.signin)):
    return ret['token']


@app.post('/user/signup-with-json')
async def signup_with_json(
    user=Depends(fba.action('signup', method='json', username_field='email')),
):
    return user


@app.post('/user/signin-with-json')
async def signin_with_json(
    ret=Depends(fba.action('signin', method='json', username_field='email')),
):
    return ret['token']


@app.post('/user/signup-with-extra-fields')
async def signup_with_extra_fields(
    user=Depends(fba.action('signup', method='json', extra_fields=['email'])),
):
    return user


# fba.get_current_user resolve to User object or a HTTP 401 response
@app.get('/user/me')
async def me(user=Depends(fba.get_current_user)):
    return user
