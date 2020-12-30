import os , sys
o_path = os.getcwd()
sys.path.append(os.path.split(o_path)[0])
import pytest , json
from aiohttp import web
from aiohttp_jwtplus import (
    SecretManager,
    JWTHelper,
    basic_identifier,
    basic_token_getter,
    show_request_info
)

async def index(request):
    carry = request['auth_carry']
    return web.json_response(carry)

async def bear(request):
    carry = request['auth_carry']['username']
    return web.Response(text = carry)

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
        unauthorized_return_route = '' , 
        unauthorized_return_route_handler = index,
        authorized_return_page_handler = index,
        secret_manager = secret_manager , 
        token_getter = basic_token_getter,  
        identifier =  basic_identifier ,   
        whitelist = () , 
        protected_apis = [] 
    )
    app = web.Application(
        middlewares=[ 
            jwt.pre_jwt_identifier(),
            jwt.post_jwt_router(),
        ]
    )
    app.router.add_get('/index.html' , index)
    app.router.add_get('/bear' ,bear)
    return loop.run_until_complete(aiohttp_client(app))

async def test_idnt(cli):
    secret_manager = SecretManager( secret = 'testsecret' )
    jwt = secret_manager.encode({'username' : 'jacky'})
    headers = {
        'Authorization': "Bearer " + jwt
    }

    resp = await cli.get('/index.html' , headers = headers)
    assert resp.status == 200
    r_json = json.loads(await resp.text())
    assert 'username' in r_json
    assert r_json['username'] == 'jacky'
    assert r_json['full_jwt_payload'] == secret_manager.decode(jwt , 'testsecret')

    resp = await cli.get('/index.html')
    assert resp.status == 200
    r_json = json.loads(await resp.text())
    assert r_json == None

async def test_unicode(cli):
    secret_manager = SecretManager( secret = 'testsecret' )
    jwt = secret_manager.encode({'username' : '你好世界'})
    headers = {
        'Authorization': "Bearer " + jwt
    }

    resp = await cli.get('/index.html' , headers = headers)
    assert resp.status == 200
    r_json = json.loads(await resp.text())
    assert 'username' in r_json
    assert r_json['username'] == '你好世界'

    resp = await cli.get('/bear' , headers = headers)
    assert resp.status == 200
    assert await resp.text() == '你好世界'