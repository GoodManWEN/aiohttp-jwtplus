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

global_secret = ...

async def authorised(request):
    return web.Response(text = 'pass')

async def unauthorised(request):
    return web.Response(text = 'fail')


@pytest.fixture
def cli(loop, aiohttp_client):
    global global_secret
    secret_manager = SecretManager( secret = 'testsecret' ,    
                                    refresh_interval = '1s' , 
                                    scheme = "Bearer" ,  
                                    algorithm = 'HS256' ,     
                                    exptime = '2s' ,     
                                    )
    global_secret = secret_manager
    jwt = JWTHelper(
            unauthorized_return_route = '' , 
            unauthorized_return_route_handler = unauthorised,
            authorized_return_page_handler = authorised,
            secret_manager = secret_manager 
        )
    app = web.Application(middlewares=[ 
                jwt.pre_jwt_identifier(),
                jwt.post_jwt_router(),
                                ])
    app.router.add_get('/index.html' , authorised)
    app.router.add_get('/login.html' , unauthorised)
    loop.create_task(secret_manager.auto_refresh())
    return loop.run_until_complete(aiohttp_client(app))


async def test_with_auth(cli):
    secret_selected = global_secret.get_secrets()[0]
    secret_manager = SecretManager( secret = secret_selected)
    jwt = secret_manager.encode({'username' : 'jacky'})
    headers = {
        'Authorization': "Bearer " + jwt.decode()
    }

    resp = await cli.get('/index.html' , headers = {})
    assert resp.status == 200
    assert await resp.text() == "fail"

    await asyncio.sleep(0.5)
    resp = await cli.get('/index.html' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == "pass"

    await asyncio.sleep(1)
    resp = await cli.get('/index.html' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == "pass"

    await asyncio.sleep(1)
    resp = await cli.get('/index.html' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == "fail"

    assert secret_selected != global_secret.get_secrets()[0]