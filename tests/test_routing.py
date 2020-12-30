import os , sys
o_path = os.getcwd()
sys.path.append(os.path.split(o_path)[0])
import pytest
from aiohttp import web
from aiohttp_jwtplus import (
    SecretManager,
    JWTHelper,
    basic_identifier,
    basic_token_getter,
    show_request_info
)

async def main_spa_page(request):
    return web.Response(text="this is index.html")

async def login_spa_page(request):
    return web.Response(text="this is login.html")

async def loginapi(request):
    return web.Response(text="loginapi called")

async def setattr_(request):
    return web.Response(text= 'this is a procted api')

@pytest.fixture
def cli(loop, aiohttp_client):
    secret_manager = SecretManager( 
        secret = 'testsecret' ,    
        refresh_interval = '30d' , 
        scheme = "Bearer" ,  
        algorithm = 'HS256' ,     
        exptime = '30d' ,     
    )
    jwt = JWTHelper(
        unauthorized_return_route = '/login.html' , 
        unauthorized_return_route_handler = login_spa_page,
        authorized_return_page_handler = main_spa_page,
        secret_manager = secret_manager , 
        token_getter = basic_token_getter,  
        identifier =  basic_identifier ,   
        whitelist = ('/authentication', ) , 
        protected_apis = ['/setattr',] 
    )
    app = web.Application(
        middlewares=[ 
            jwt.pre_jwt_identifier(),
            jwt.post_jwt_router(),
        ]
    )
    app.router.add_get('/index.html' , main_spa_page)
    app.router.add_get('/login.html' , login_spa_page)
    app.router.add_get('/authentication', loginapi)
    app.router.add_get('/setattr', setattr_)

    return loop.run_until_complete(aiohttp_client(app))

async def test_without_auth(cli):
    resp = await cli.get('/index.html')
    assert resp.status == 200
    assert await resp.text() == "this is login.html"

    resp = await cli.get('/login.html')
    assert resp.status == 200
    assert await resp.text() == "this is login.html"

    resp = await cli.get('/authentication')
    assert resp.status == 200
    assert await resp.text() == "loginapi called"

    resp = await cli.get('/setattr')
    assert resp.status == 401

    resp = await cli.get('/404')
    assert resp.status == 200
    assert await resp.text() == "this is login.html"

async def test_with_auth(cli):
    secret_manager = SecretManager( secret = 'testsecret' )
    jwt = secret_manager.encode({'username' : 'jacky'})
    headers = {
        'Authorization': "Bearer " + jwt
    }

    resp = await cli.get('/index.html' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == "this is index.html"

    resp = await cli.get('/login.html' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == "this is index.html"

    resp = await cli.get('/authentication' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == "loginapi called"

    resp = await cli.get('/setattr' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == "this is a procted api"

    resp = await cli.get('/404' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == "this is index.html"

async def test_with_wrong_auth(cli):
    secret_manager = SecretManager( secret = 'testsecret' )
    jwt = secret_manager.encode({'username' : 'jacky'})
    wrong_headers = {
        'Authorization': "Bearer " + jwt[:-1]
    }

    resp = await cli.get('/index.html' , headers = wrong_headers)
    assert resp.status == 200
    assert await resp.text() == "this is login.html"

    resp = await cli.get('/login.html' , headers = wrong_headers)
    assert resp.status == 200
    assert await resp.text() == "this is login.html"

    resp = await cli.get('/authentication' , headers = wrong_headers)
    assert resp.status == 200
    assert await resp.text() == "loginapi called"

    resp = await cli.get('/setattr' , headers = wrong_headers)
    assert resp.status == 403

    resp = await cli.get('/404' , headers = wrong_headers)
    assert resp.status == 200
    assert await resp.text() == "this is login.html"

async def test_with_exped_auth(cli):
    secret_manager = SecretManager( secret = 'testsecret' ,
                                    exptime = -1
                                    )
    jwt = secret_manager.encode({'username' : 'jacky'})
    headers = {
        'Authorization': "Bearer " + jwt
    }

    resp = await cli.get('/index.html' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == "this is login.html"

    resp = await cli.get('/login.html' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == "this is login.html"

    resp = await cli.get('/authentication' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == "loginapi called"

    resp = await cli.get('/setattr' , headers = headers)
    assert resp.status == 403

    resp = await cli.get('/404' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == "this is login.html"
