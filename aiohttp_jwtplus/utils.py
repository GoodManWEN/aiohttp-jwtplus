from aiohttp import web

async def basic_token_getter(request):
    headers = request.headers
    if 'Authorization' not in headers:
        return web.HTTPUnauthorized()
    else:
        try:
            scheme , token = request.headers.get('Authorization').strip().split(' ')
            assert scheme == 'Bearer'
            return token
        except:
            return web.HTTPForbidden()

async def basic_identifier(payload):
    if 'username' in payload:
        ret = payload['username']
        if ret:
            return {'username' : ret , 'full_jwt_payload':payload}
    else:
        return False

def show_request_info(request):
    print('/*')
    print("handler of request is triggered")
    print(f"\trequest path  :\t{request.path}")
    print(f"\tauthen status :\t{request['auth_status']}")
    print(f"\tcarry words   :\t{request['auth_carry']}")
    print("\t\t\t*/")
    
