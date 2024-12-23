#!/usr/bin/env python
# coding: utf-8
# yc@2020/08/27

from pydantic import BaseModel


class Token(BaseModel):
    token_type: str = 'bearer'
    access_token: str
