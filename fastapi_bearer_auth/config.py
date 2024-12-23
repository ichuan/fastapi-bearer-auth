#!/usr/bin/env python
# coding: utf-8
# yc@2020/08/27

import inspect

_config = {}


def get(key):
    return _config[key]


def set(key, value):
    _config[key] = value
    return value


async def call(name, *args, **kwargs):
    fn = get(name)
    if inspect.iscoroutinefunction(fn):
        return await fn(*args, **kwargs)
    return fn(*args, **kwargs)
