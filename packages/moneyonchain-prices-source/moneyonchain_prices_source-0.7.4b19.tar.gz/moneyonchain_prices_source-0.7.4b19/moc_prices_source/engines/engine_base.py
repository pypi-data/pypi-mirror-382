import requests, datetime, json, sys
from os.path import basename, dirname, abspath
from decimal import Decimal
from coins import *
from bs4 import BeautifulSoup
from web3 import Web3, HTTPProvider
from os import environ
from requests import Response

base_dir = dirname(dirname(abspath(__file__)))
bkpath   = sys.path[:]
sys.path.insert(0, dirname(base_dir))

#FIXME: this is a workaround for circular import, this is horrible, fix it later
try: 
    from moc_prices_source.redis_conn import get_redis
except ImportError:
    def get_redis():
        return None

sys.path = bkpath

app_name = basename(base_dir)



class Base(object):

    _name                          = "base"
    _description                   = "Base Engine"
    _method                        = 'get'
    _uri                           = "http://api.pricefetcher.com/BTCUSD"
    _payload                       = {}
    _headers                       = {}
    _coinpair                      = BTC_USD
    _timeout                       = 10
    _max_age                       = 30
    _max_time_without_price_change = 180 # zero means infinity
    _redis_expiration              = 3600
    _ssl_verify                    = True
    _rq_side_cache_time            = 3    



    @property
    def name(self):
        return self._name


    @property
    def description(self):
        return self._description


    @property
    def uri(self):
        return self._uri


    @property
    def coinpair(self):
        return self._coinpair


    @property
    def timeout(self):
        return self._timeout


    def _clean_output_values(self):
        self._price                 = None
        self._volume                = None
        self._timestamp             = None
        self._last_change_timestamp = None
        self._error                 = None
        self._time                  = None
        self._age                   = None


    def __init__(self, session=None, session_storage=None):
        self._redis = get_redis()
        self._engine_session_id = app_name + '/' + self._name
        self._session_storage = session_storage
        self._session = session
        self._clean_output_values()


    @property
    def price(self):
        return self._price


    @property
    def volume(self):
        return self._volume


    @property
    def age(self):
        return self._age


    @property
    def max_age(self):
        return self._max_age


    @property
    def timestamp(self):
        return self._timestamp

    @property
    def last_change_timestamp(self):
        return self._last_change_timestamp

    @property
    def error(self):
        return self._error


    @property
    def time(self):
        return self._time


    @staticmethod
    def _name_from_file(_file):
        name = basename(_file)
        if name.endswith('.py'):
            name = name[:-3]
        return name


    @staticmethod
    def _now():
        return datetime.datetime.now().replace(microsecond=0)


    @staticmethod
    def _utcfromtimestamp(timestamp):
        return datetime.datetime.utcfromtimestamp(int(timestamp))


    def _map(self, data):
        return {
            'price':  data['last'],
            'volume': data['volume'],
            'timestamp': self._utcfromtimestamp(data['timestamp']) }


    def _json(self, response):
        out = None
        try:
            out = response.json()
        except Exception:
            self._error = "Response format error (not JSON)"
        return out


    def __bool__(self):
        return not(bool(self._error))


    def __str__(self):
        name  = '{} {}'.format(self.description, self.coinpair
            ) if self.description else self.name
        if self.price is None:
            return name
        value = self.price if self else self.error
        return '{} = {}'.format(name, value)


    @property
    def as_dict(self):
        out = {}
        for attr in [
            'coinpair',
            'description',
            'error',
            'name',
            'price',
            'timeout',
            'timestamp',
            'last_change_timestamp',
            'uri',
            'volume',
            'time',
            'age']:
            out[attr] = getattr(self, attr, None)
        out['ok'] = bool(self)
        return out


    @property
    def as_json(self):
        data = self.as_dict
        for k in data.keys():
            if k in data:
                v = data[k]
                if isinstance(v, Decimal):
                    data[k] = float(v)
                if isinstance(v, datetime.datetime):
                    data[k] = datetime.datetime.timestamp(v)
                elif v!=None and not(isinstance(v, (int, bool, float))):
                    data[k] = str(v)
        return json.dumps(data, indent=4, sort_keys=True)


    def _request(self, rq):

        method = self._method.strip().lower()
        if method=='post':
            getter = rq.post
        else:
            getter = rq.get

        kargs = {'url':self.uri, 'timeout': self.timeout, 'verify': self._ssl_verify}
        if self._payload:
            kargs['data'] = self._payload
        if self._headers:
            kargs['headers'] = self._headers

        self._clean_output_values()

        response = None

        if self._redis is not None:

            cache_key_dict = kargs.copy()
            cache_key_dict['method'] = method
            cache_key = \
                f"RQCACHE({json.dumps(cache_key_dict, sort_keys=True)})"
            
            try:
                cached_response = json.loads(self._redis.get(cache_key))
            except Exception as e:
                cached_response = None
            
            if cached_response:
                response = Response()
                try:
                    response.status_code = cached_response["status_code"]
                    response._content = cached_response["content"].encode()
                    response.headers = cached_response["headers"]
                    response.url = cached_response["url"]
                except Exception as e:
                    response = None

        if response is None:

            try:
                response = getter(**kargs)
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                self._error = e
                return None
            except Exception as e:
                self._error = e
                return None

            if not response:
                self._error = "No response from server"
                return None

            if response.status_code != 200:
                self._error = "Response error (code {})".format(
                    response.status_code)
                return None

            try:
                self._age = int(response.headers['age'])
            except ValueError:
                self._age = None
            except KeyError:
                self._age = None

            if self._age!=None and self._age > self._max_age:
                self._error = str(f"Response age error (age > {self._max_age})")
                return None
            
            if self._redis is not None:

                response_to_cache_str = json.dumps({
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "content": response.text,
                    "url": response.url}, indent=4)
                
                time = datetime.timedelta(seconds=self._rq_side_cache_time)
                self._redis.setex(cache_key, time, response_to_cache_str)
        
        response = self._json(response)

        if not response:
            return None

        return response


    def __call__(self, start_time=None):

        if start_time is None:
            start_time = datetime.datetime.now()

        rq = requests if self._session is None else self._session

        response = self._request(rq)
 
        if not response:
            if not self._error:
                self._error = "Empty response from server"
            return False

        self._error = None
        try:
            info = self._map(response)
            self._price = Decimal(str(info['price']))
        except Exception:
            if self._error is None:
                self._error = "Engine error (bad mapping) trying to get 'price'"
            return False
        
        if not self._price:
            self._error = "No price"
            return False

        if 'timestamp' in info:
            if isinstance(info['timestamp'], datetime.datetime):
                self._timestamp = info['timestamp']
            else:
                self._error = "Engine error (bad mapping) trying to get 'timestamp'"
                return False
        else:
            self._timestamp = self._now()
        self._last_change_timestamp = self._timestamp

        if 'volume' in info:
            try:
                self._volume = Decimal(str(info['volume']))
            except Exception:
                self._error = "Engine error (bad mapping)  trying to get 'volume'"
                return False
        else:
            self._volume = 0.0

        self._time = datetime.datetime.now() - start_time

        if self._redis is not None or isinstance(self._session_storage, dict):

            session_id = self._engine_session_id

            if self._max_time_without_price_change:

                if self._redis is not None:
                    try:
                        pre_data = json.loads(self._redis.get(session_id))
                    except Exception:
                        pre_data = {}
                elif isinstance(self._session_storage, dict):
                    try:
                        pre_data = self._session_storage[session_id]
                    except Exception:
                        pre_data = {}
                if not isinstance(pre_data, dict):
                    pre_data = {}

                try:
                    pre_last_change_timestamp = datetime.datetime.fromtimestamp(pre_data['last_change_timestamp'])
                except Exception:
                    pre_last_change_timestamp = None

                try:
                    pre_price = Decimal(pre_data['price'])
                except Exception:
                    pre_price = None

                if pre_price!=None and pre_last_change_timestamp!=None:
                    if pre_price==self._price:
                        self._last_change_timestamp = pre_last_change_timestamp

                max_time_without_price_change = datetime.timedelta(seconds=self._max_time_without_price_change)
                time_without_price_change     = datetime.datetime.now()-self._last_change_timestamp

                if time_without_price_change > max_time_without_price_change:
                    self._error = str(f"Too much time without price change (t > {max_time_without_price_change})")
                    return False

            if self._redis is not None:
                time = datetime.timedelta(seconds=self._redis_expiration)
                self._redis.setex(session_id, time, self.as_json)
            elif isinstance(self._session_storage, dict):
                self._session_storage[session_id] = self.as_dict

        return True


class EngineWebScraping(Base):

    def _scraping(self, html):
        value = None
        if not value:
            self._error = "Response format error"
            return None
        return {
            'price':  value
        }

    def _json(self, response):
        html = BeautifulSoup(response.text, 'lxml')
        data = self._scraping(html)
        if self._error: 
            self._error += " (Web scraping)"
        return data

    def _map(self, data):
        return data


class BaseWithFailover(Base):

    _uri_failover = None

    def __call__(self, start_time=None):
        if start_time is None:
            start_time = datetime.datetime.now()
        ok = Base.__call__(self, start_time)
        if self._uri_failover and not ok:
            uri_failover, uri = self._uri_failover, self._uri
            self._uri_failover, self._uri =  uri, uri_failover
            ok = Base.__call__(self, start_time)
        return ok


class BaseOnChain(Base):

    erc20_simplified_abi = """
[
    {
        "constant": true,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "balance",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    }
]
"""
    Web3 = Web3
    HTTPProvider = HTTPProvider

    def to_checksum_address(self, value):
        try:
            return self.Web3.to_checksum_address(value)
        except:
            return self.Web3.toChecksumAddress(value)
    
    def make_web3_obj_with_uri(self):
        return self.Web3(self.HTTPProvider(self._uri))

    def _get_price(self):

        try:

            return 0

        except Exception as e:
            self._error = str(e)
            return None


    def __call__(self, start_time=None):

        if start_time is None:
            start_time = datetime.datetime.now()

        price = None

        if self._redis is not None:

            cache_key = f"RQ_ONCHAIN_CACHE({self._name})"

            price = self._redis.get(cache_key)

            try:
                price = self._redis.get(cache_key)
            except Exception as e:
                price = None
            
            price = None if price is None else price.decode('utf-8')

        if price is None:

            price = self._get_price()
    
            if not price:
                if not self._error:
                    self._error = "Engine error trying to get 'price'"
                return False
            
            if self._redis is not None:
                time = datetime.timedelta(seconds=self._rq_side_cache_time)
                self._redis.setex(cache_key, time, str(price))

        try:
            self._price = Decimal(str(price))
        except Exception:
            self._error = "Engine error trying to get 'price'"
            return False

        self._timestamp = self._now()
        self._last_change_timestamp = self._timestamp

        self._volume = 0.0
        self._time = datetime.datetime.now() - start_time

        return True


def get_env(name, default):
    try:
        return str(environ[name])
    except KeyError :
        return default
    


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
