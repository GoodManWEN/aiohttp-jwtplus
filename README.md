# aiohttp-jwtplus
Aiohttp middleware and helper utils for working with JSON web token.
Added a post router for improving security level of SPAs &amp; auto refresh secrets.

- Works on Python3.7+

## Requirements
- [Aiohttp >= 2.3.5](https://github.com/aio-libs/aiohttp)
- [PyJWT](https://github.com/jpadilla/pyjwt)

## Install

    not uploaded yet.

## Usage
- You need to create a SecretManager object ,which manages informations(secret \ scheme \ algorithm \ exp_interval \ auto_refresh_interval etc.) about jwt first.
- Then you need to create a JWTHelper ,in whose slots you can  definite your business logic ,such as where you get token from ,what you do in identify process etc. If you dont pass them in ,JWTHelper will provides you a basic version of token_getter & identifier ,which simplely gets token from headers['Authorization'] value and then check out if decoded dictionary has key value 'username'.
- Finally you can create aiohttp.web.Application and pass middlewares in . It's a necessary condition to passin pre_jwt_identification() and post_jwt_router() in order if you would like to activate post router. It's no need to register middleware via decorator first.

## Behaviors of routing under different authorization
path | remarks | authorized destination |  unauthorized destination
-|-|-|-
/index.html | Entry of main functional SPA | /index.html | /login.html
/login.html | Entry of login page. Independent SPA | /index.html | /login.html
/login_api  | Login api , one in jwt whitelist. | /login_api | login_api
/setattr_api | One of protected apis. | /setattr_api | 403 or 401
/404        | Undefined page | /index.html | /login.html

## Example

