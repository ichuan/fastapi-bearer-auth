#!/usr/bin/env python
# coding: utf-8
# yc@2020/08/28


from fastapi import Depends, Form, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from . import auth, config, models


async def _signup(request: Request, username: str, password: str):
    if await config.call('get_user_by_name', username):
        raise HTTPException(status_code=400, detail='Username exists')
    try:
        return await config.call('create_user', username, password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def signup_with_form(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    return await _signup(request, username, password)


async def signup_with_json(request: Request, user: models.User):
    return await _signup(request, user.username, user.password)


async def _signin(request: Request, form: OAuth2PasswordRequestForm | models.User):
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


async def signin_with_form(
    request: Request, form: OAuth2PasswordRequestForm = Depends()
):
    return await _signin(request, form)


async def signin_with_json(request: Request, form: models.User):
    return await _signin(request, form)


# default to form
signup = signup_with_form
signin = signin_with_form
