#!/usr/bin/env python
# coding: utf-8
# yc@2020/08/27


from . import config
from . import defaults
from .auth import get_current_user  # noqa: F401
from .router import user_router  # noqa: F401


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
        if not i.startswith(('handle_', 'before_', 'after_')):
            config.set(i, j)


set_config(defaults.consts)


def call_config(key, *args, **kwargs):
    return config.call(key, *args, **kwargs)


def on_event(name):
    def decorator(fn):
        config.set(name, fn)
        return fn

    return decorator


for k in (
    'before_user_signup',
    'after_user_signup',
    'before_user_signin',
    'after_user_signin',
):
    config.set(k, getattr(defaults, k))
