import datetime
import random
from collections import deque
import jwt as pyjwt
import re
import asyncio

class SecretManager:

    def __init__(self , 
                secret:str = "" , 
                refresh_interval = 0 , 
                scheme = 'Bearer',
                algorithm = 'HS256' , 
                exptime = '30d'
                ):
        if not isinstance(secret , str):
            raise TypeError("Secret should be a string.")

        self.algorithm = algorithm
        self._secrets = deque()
        if secret:
            self._secret_length = len(secret)
            self._secrets.append(secret)
        else:
            self._secret_length = 32
            self._secrets.append(self._random_token(self._secret_length))
        self._refresh_interval = self._parse_time(refresh_interval)
        self._exptime = self._parse_time(exptime)
        self.scheme = scheme
        self._scheme_bytes = self.scheme.encode('utf-8')

    def _parse_time(self, interval):  

        convert_table = {
            'd': 86400,
            "h": 3600,
            'm': 60,
            's': 1
        }

        try:
            if isinstance(interval,str):
                if interval.isdigit():
                    rtv = int(interval)
                else:
                    assert len(interval) > 0
                    assert interval[-1] in convert_table
                    matched = re.match(r'[\d]*[\.]?[\d]+',interval[:-1])
                    assert matched
                    assert matched.span()[1] == len(interval[:-1])
                    rtv = int(float(interval[:-1]) * \
                        convert_table[interval[-1]])
            else:
                assert isinstance(interval,int)    or isinstance(interval,float)
                rtv = interval
            # assert rtv >= 0
            return rtv
        except:
            raise RuntimeError("Invalid interval setted.")
    

    def _random_token(self , n):
        rc = lambda :chr(random.randint(0,74) + 48)
        return ''.join((rc() for i in range(n)))

    def decode(self , *args , **kwargs):
        return pyjwt.decode( algorithm = self.algorithm ,*args , **kwargs)

    def encode(self , payload , *args , **kwargs):
        if not isinstance(payload , dict):
            raise RuntimeError('payload must be a dictionary.')
        headers = {
            "typ": "JWT",
            "alg": self.algorithm,
        }
        payload_ = {
            "headers": headers,
            'iat': datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=self._exptime),
        }
        payload_.update(payload)
        return pyjwt.encode(payload_ , self._secrets[-1] , algorithm = self.algorithm , *args , **kwargs)

    def get_secrets(self):
        return tuple(self._secrets)

    async def auto_refresh(self):

        async def _remove_in_time(time , tk):
            await asyncio.sleep(time)
            self._secrets.remove(tk)

        loop = asyncio.get_running_loop()
        current_tk = self._secrets[0]
        loop.create_task(_remove_in_time(self._exptime , current_tk))

        if self._refresh_interval > 0:
            while True:
                await asyncio.sleep(self._refresh_interval)
                new_tk = self._random_token(self._secret_length)
                self._secrets.append(new_tk) 
                loop.create_task(_remove_in_time(self._exptime * 2 , new_tk))
