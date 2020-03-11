import os , sys
o_path = os.getcwd()
sys.path.append(os.path.split(o_path)[0])
import pytest
import asyncio
from aiohttp import web
from aiohttp_jwtplus import (
    SecretManager,
    JWTHelper,
    basic_identifier,
    basic_token_getter,
    show_request_info
)

async def public_css1(request):
    return web.Response(text = 'css1')

async def public_css2(request):
    return web.Response(text = 'css2')

async def authorised(request):
    return web.Response(text = 'pass')

async def unauthorised(request):
    return web.Response(text = 'fail')


@pytest.fixture
def cli(loop, aiohttp_client):
    secret_manager = SecretManager( secret = 'testsecret')
    global_secret = secret_manager
    jwt = JWTHelper(
            unauthorized_return_route = '' , 
            unauthorized_return_route_handler = unauthorised,
            authorized_return_page_handler = authorised,
            secret_manager = secret_manager ,
            whitelist = ('/css/.+',)
        )
    app = web.Application(middlewares=[ 
                jwt.pre_jwt_identifier(),
                jwt.post_jwt_router(),
                                ])
    app.router.add_get('/index.html' , authorised)
    app.router.add_get('/login.html' , unauthorised)
    app.router.add_get('/css/1.css' , public_css1)
    app.router.add_get('/css/2.css' , public_css2)
    loop.create_task(secret_manager.auto_refresh())
    return loop.run_until_complete(aiohttp_client(app))


async def test_with_auth(cli):
    secret_manager = SecretManager( secret = 'testsecret')
    jwt = secret_manager.encode({'username' : 'jacky'})
    headers = {
        'Authorization': "Bearer " + jwt.decode()
    }

    resp = await cli.get('/css/1.css' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == 'css1'

    resp = await cli.get('/css/2.css' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == 'css2'

    resp = await cli.get('/css/3.css' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == 'pass'

    resp = await cli.get('/css/3.css' , headers = {})
    assert resp.status == 200
    assert await resp.text() == 'fail'

    resp = await cli.get('/css/1.css' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == 'css1'