# FastAPI Bearer Auth

A simple FastAPI auth module implementing [OAuth2 with Password (and hashing), Bearer with JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/), including user signup, signin routes.


## Installing

Works on python3.6+

```shell
pip install fastapi-bearer-auth
```


## Example of using

```python
from fastapi import FastAPI

import fastapi_bearer_auth as fba


app = FastAPI(title='Test App')
app.include_router(fba.user_router, prefix='/user', tags=['User'])


# simple in-memory db
users = {}


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
```

Now head to http://127.0.0.1:8000/docs to test the API.

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
