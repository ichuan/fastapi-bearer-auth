#!/usr/bin/env python
# coding: utf-8
# yc@2020/08/27

from fastapi import FastAPI, Depends

import fastapi_bearer_auth as fba


app = FastAPI(title='Test App')
app.include_router(fba.user_router, prefix='/user', tags=['User'])


users = {}


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


@app.get('/test')
async def test(user: dict = Depends(fba.get_current_user)):
    return user
