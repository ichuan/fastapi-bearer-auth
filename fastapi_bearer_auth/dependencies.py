#!/usr/bin/env python
# coding: utf-8
# yc@2020/08/28


from fastapi import Depends, Form, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from . import config
from . import auth


async def signup(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    if await config.call('get_user_by_name', username):
        raise HTTPException(status_code=400, detail='Username exists')
    try:
        return await config.call('create_user', username, password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def signin(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    user = await config.call('authenticate', form.username, form.password)
    if user is None:
        raise HTTPException(status_code=400, detail='Invalid username or password')
    return {
        'user': user,
        'token': {
            'token_type': 'bearer',
            'access_token': await auth.create_access_token(user),
        },
    }
