#!/usr/bin/env python
# coding: utf-8
# yc@2020/08/27


from . import config, defaults
from .auth import get_current_user  # noqa: E402, F401
from .dependencies import (  # noqa: E402, F401
    action,
    signin,
    signup,
)

for k in (
    'get_user_by_name',
    'authenticate',
    'verify_password',
    'get_password_hash',
    'create_user',
):
    config.set(k, getattr(defaults, k))
    globals()['handle_{}'.format(k)] = lambda fn, key=k: config.set(key, fn)


def set_config(consts):
    for i, j in consts.items():
        if not i.startswith('handle_'):
            config.set(i, j)


set_config(defaults.consts)


def call_config(key, *args, **kwargs):
    return config.call(key, *args, **kwargs)
