# FastAPI Bearer Auth

A simple FastAPI auth module implementing [OAuth2 with Password (and hashing), Bearer with JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/), including user signup, signin routes.


## Installing

Works on python3.6+

```shell
pip install fastapi-bearer-auth
```


## Example of using

```python
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
```

Now head to http://127.0.0.1:8000/docs to test the API. Note the `me` route, using `fba.get_current_user` dependency to restrict resource for authenticated user.

There's a simple command to achive this without writing any code:

```shell
uvicorn fastapi_bearer_auth.test:app
```


## Customize

In addition to `get_user_by_name(name)` and `create_user(username, password)`, there're other functions can be override (with `handle_` prefix):

- `authenticate(username, password)`
- `verify_password(plain_password, hashed_password)`
- `get_password_hash(password)`

You can call all those functions with `fba.call_config(name, *args, **kwargs)`.


Also some params:

- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `ALGORITHM`
- `SECRET_KEY`

Use something like `fba.set_config({'SECRET_KEY': 'xxx', ...})` to change it.


The default tokenUrl for openapi docs is `user/signin`, you can override this by setting env var `TOKEN_URL`.
