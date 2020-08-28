#!/usr/bin/env python
# coding: utf-8
# yc@2020/08/27

from pydantic import BaseModel
from fastapi import FastAPI, Depends

import fastapi_bearer_auth as fba


class UserOut(BaseModel):
    username: str


app = FastAPI(title='Test App')
# simple in-memory db
users = {}


# Two required handler: handle_get_user_by_name and handle_create_user
@fba.handle_get_user_by_name
async def get_user_by_name(name):
    return users.get(name)


@fba.handle_create_user
async def create_user(username, password):
    if await get_user_by_name(username):
        raise ValueError('Username {} exists'.format(username))
    user = {
        'username': username,
        'password': await fba.call_config('get_password_hash', password),
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


# fba.get_current_user resolve to User object or a HTTP 401 response
@app.get('/user/me', response_model=UserOut)
async def me(user=Depends(fba.get_current_user)):
    return user
