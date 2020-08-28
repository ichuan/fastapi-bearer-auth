#!/usr/bin/env python
# coding: utf-8
# yc@2020/08/27

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from . import config
from . import auth
from . import models


user_router = APIRouter()


@user_router.post('/signup', response_model=models.UserOut)
async def signup(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    try:
        await config.call('before_user_signup', request, username, password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=e.args[0])
    if await config.call('get_user_by_name', username):
        raise HTTPException(status_code=400, detail='Username exists')
    try:
        user = await config.call('create_user', username, password)
        await config.call('after_user_signup', request, user)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@user_router.post('/signin', response_model=models.Token)
async def signin(request: Request, form: OAuth2PasswordRequestForm = Depends()):
    try:
        await config.call('before_user_signin', request, form.username, form.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=e.args[0])
    user = await config.call('authenticate', form.username, form.password)
    if user is None:
        raise HTTPException(status_code=400, detail='Invalid username or password')
    try:
        await config.call('after_user_signin', request, user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=e.args[0])
    return {
        'token_type': 'bearer',
        'access_token': await auth.create_access_token(user),
    }


@user_router.post('/me', response_model=models.UserOut)
async def me(user: dict = Depends(auth.get_current_user)):
    return user
