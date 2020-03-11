from .secrets import SecretManager
from .utils import basic_token_getter ,basic_identifier
from aiohttp import web
import logging
import re

logger = logging.getLogger(__name__)

class JWTHelper:

    def __init__(self , 
        unauthorized_return_route , # this's an exception which means if you've alreadly logined ,you cannot access to this page. 
        unauthorized_return_route_handler,
        authorized_return_page_handler,
        secret_manager = None , 
        token_getter = None , 
        identifier = None ,
        whitelist = () , 
        protected_apis = [] 
        ):
        if not isinstance(whitelist , tuple):
            raise TypeError(f'whitelist must be a tuple')

        self._whitelist = whitelist
        self.protected_apis = protected_apis
        self._unauthorized_return_route = unauthorized_return_route
        self._unauthorized_return_route_handler = unauthorized_return_route_handler
        self._authorized_return_page_handler = authorized_return_page_handler
    
        if secret_manager:
            if not isinstance(secret_manager , SecretManager):
                raise TypeError(f'secret_manager shoud be a {type(SecretManager)} type object.')
            self._secret_manager = secret_manager
        else:
            self._secret_manager = SecretManager()

        if token_getter:
            self._token_getter = token_getter
        else:
            self._token_getter = basic_token_getter

        if identifier:
            self._identifier = identifier
        else:
            self._identifier = basic_identifier

    def pre_jwt_identifier(self , *args , **kwargs):
        
        @web.middleware
        async def _jwtplus(request , handler):

            request['auth_carry'] = None
            getted_jwt = await self._token_getter(request)

            if isinstance(getted_jwt , web.HTTPException):
                request['auth_status'] = getted_jwt.__class__.__name__[4:]
            else:
                secrets = self._secret_manager.get_secrets()
                for secret in secrets:
                    try:                      
                        payload = self._secret_manager.decode( getted_jwt , 
                                    secret , 
                                    )
                        ret = await self._identifier(payload)
                        assert ret
                        request['auth_status'] = "pass"
                        request['auth_carry'] = ret
                        break
                    except:
                        continue
                else:
                    # authorization failed
                    request['auth_status'] = 'Forbidden'
            return await handler(request)

        return _jwtplus


    def post_jwt_router(self , *args , **kwargs):

        def check_if_request_in_whitelist(path , whitelist):
            for pattern in whitelist:
                matched = re.match(pattern , path)
                if matched and matched.span()[1] == len(path):
                    return True
            return False

        @web.middleware
        async def _router(request, handler):
            try:

                if self._whitelist:
                    if check_if_request_in_whitelist(request.path , self._whitelist):
                        return await handler(request)
                # handler request part.
                if request['auth_status'] == 'pass':
                    if request.path == self._unauthorized_return_route:
                        response = await self._authorized_return_page_handler(request)
                    else:
                        response = await handler(request)
                else:
                    if request.path in self.protected_apis:
                        response = getattr(web , f'HTTP{request["auth_status"]}')()
                    else:
                        response = await self._unauthorized_return_route_handler(request)

            except web.HTTPException as ex:
                if ex.status != 404:
                    logger.exception(ex, exc_info=ex)
                    raise ex
                if request['auth_status'] == 'pass':
                    response = await self._authorized_return_page_handler(request)
                else:
                    response = await self._unauthorized_return_route_handler(request)

            return response
            
        return _router

    def get_secret_manager(self):
        return self._secret_manager

    def white_list_append(self,other):
        tup = list(self._whitelist)
        tup.append(other)
        self._whitelist = tuple(tup)

    def white_list_remove(self,other):
        tup = list(self._whitelist)
        tup.remove(other)
        self._whitelist = tuple(tup)

    def test_behav(self):
        '''
        more information in test_behav.py
        '''
        pass


