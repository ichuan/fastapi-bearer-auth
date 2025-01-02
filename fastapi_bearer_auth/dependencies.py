#!/usr/bin/env python
# coding: utf-8
# yc@2020/08/28


from typing import Annotated, Literal

from fastapi import Depends, Form, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, create_model

from . import auth, config
from .defaults import create_user


async def _signup(
    request: Request,
    username: str,
    password: str,
    username_field: str = 'username',
    **extra_fields,
):
    if await config.call('get_user_by_name', username, **extra_fields):
        raise HTTPException(status_code=400, detail='User exists')
    try:
        fn = config.get('create_user')
        if fn is create_user:
            return await fn(username, password, username_field, **extra_fields)
        return await fn(username, password, **extra_fields)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


async def _signin(
    request: Request,
    username: str,
    password: str,
    username_field: str = 'username',
    **extra_fields,
):
    user = await config.call('authenticate', username, password, **extra_fields)
    if user is None:
        raise HTTPException(status_code=400, detail='Invalid username or password')
    return {
        'user': user,
        'token': {
            'token_type': 'bearer',
            'access_token': await auth.create_access_token(user),
        },
    }


def action(
    action: Literal['signin', 'signup'] = 'signin',
    method: Literal['form', 'json'] = 'form',
    username_field: str = 'username',
    extra_fields: list[str] | None = None,
):
    ExtraFields = create_model(
        'ExtraFields',
        __config__=None,
        __module__=__name__,
        __doc__=None,
        __base__=BaseModel,
        __validators__=None,
        __cls_kwargs__=None,
        **{f: (str, ...) for f in (extra_fields or [])},
    )

    class UserForm(ExtraFields, BaseModel):
        username: str = Field(alias=username_field)
        password: str

    class OAuth2Form(OAuth2PasswordRequestForm):
        def __init__(self, user: Annotated[UserForm, Form()]):
            super().__init__(
                grant_type='password',
                username=user.username,
                password=user.password,
                scope='',
            )
            self._form = user

    func = {'signin': _signin, 'signup': _signup}[action]

    async def _form(request: Request, form: Annotated[OAuth2Form, Depends()]):
        return await func(
            request,
            form.username,
            form.password,
            username_field,
            **form._form.model_dump(exclude={'username', 'password'}),
        )

    async def _json(request: Request, form: UserForm):
        return await func(
            request,
            form.username,
            form.password,
            username_field,
            **form.model_dump(exclude={'username', 'password'}),
        )

    return _json if method == 'json' else _form


# default to form
signup = action('signup')
signin = action('signin')
