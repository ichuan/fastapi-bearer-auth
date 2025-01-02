# FastAPI Bearer Auth

A simple FastAPI auth module implementing [OAuth2 with Password (and hashing), Bearer with JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/), including user signup, signin routes.


## Installing

Works on python3.6+

```shell
pip install fastapi-bearer-auth
```


## Example of using

```python
from fastapi import Depends, FastAPI
from pydantic import BaseModel

import fastapi_bearer_auth as fba


class UserOut(BaseModel):
    username: str


app = FastAPI(title='Test App')
# simple in-memory db
users = {}


# Two required handler: handle_get_user_by_name and handle_create_user
@fba.handle_get_user_by_name  # type: ignore
async def get_user_by_name(name, **extra_fields):
    return users.get(name)


@fba.handle_create_user  # type: ignore
async def create_user(username, password, **extra_fields):
    if await get_user_by_name(username):
        raise ValueError('User {} exists'.format(username))
    user = {
        'username': username,
        'password': await fba.call_config('get_password_hash', password),
        **extra_fields,
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


@app.post('/user/signup-with-json')
async def signup_with_json(
    user=Depends(fba.action('signup', method='json', username_field='email')),
):
    return user


@app.post('/user/signin-with-json')
async def signin_with_json(
    ret=Depends(fba.action('signin', method='json', username_field='email')),
):
    return ret['token']


@app.post('/user/signup-with-extra-fields')
async def signup_with_extra_fields(
    user=Depends(fba.action('signup', method='json', extra_fields=['email'])),
):
    return user


# fba.get_current_user resolve to User object or a HTTP 401 response
@app.get('/user/me')
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
