import sys
from os import getenv
from os.path  import dirname, abspath
from decimal import Decimal
from fnmatch import fnmatch as match
from tabulate import tabulate
from json import dumps, loads
from flask import Flask, request, redirect, jsonify, make_response
from flask_restx import Api, Resource, reqparse, abort
from flask_cors import CORS
from flask_caching import Cache

bkpath   = sys.path[:]
base_dir = dirname(abspath(__file__))
sys.path.insert(0, dirname(base_dir))

from moc_prices_source import get_price, version
from moc_prices_source import ALL as AllCoinPairs
from moc_prices_source.cli import command, option
from moc_prices_source.redis_conn import use_redis

sys.path = bkpath


title='MoC prices source API Rest webservice'
description="""

<br>
### Description

This is the API Rest webservice that comes integrated in
the python **moc_prices_source** package.

<br>
### Purpose

Simplify integrations with other environments than **Python**.

<br>
### Refrences

* [Source code in Github](https://github.com/money-on-chain/moc_prices_source)
* [Package from Python package index (PyPI)](https://pypi.org/project/moneyonchain-prices-source)

<br>
<br>

## Endpoints
"""

def get_env_positive_int(key, default=1):
    try:
        value = int(getenv(key, default))
        if value > 0:
            return value
        else:
            raise ValueError
    except (ValueError, TypeError):
        return default

all_coinpairs = list([str(x) for x in AllCoinPairs])
max_coinpair_limit = get_env_positive_int('MAX_COINPAIR_LIMIT', 12)

app = Flask(__name__)

cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app)

def get_coin_pairs(
        wildcard: str = "*",
        coinpairs_base: list = None
        ) -> list:
    """
    Get all coin pairs that match the wildcard.
    """
    if coinpairs_base is None:
        coinpairs_base =  AllCoinPairs
    wildcards_base = str(wildcard).lower().replace(" ", ",").split(",")
    wildcards = list(set([w for w in wildcards_base if w]))
    coinpairs = []
    for w in wildcards:
        f = filter(lambda i: match(str(i).lower(), w), coinpairs_base)
        f = list(set(list(f)))
        coinpairs.extend(f)
    coinpairs = list(set(coinpairs))
    return coinpairs


class HashMethod():

    def __init__(self, *options, info=lambda x: None, pre="") -> None:
        self._pre = pre
        self.info = info
        self.options = list(map(
            lambda x: str(x).strip().lower(), list(options)))
        self.out = []

    def __call__(self, x) -> None:
        self.out = []
        for key, value in eval(x):
            key=str(key).strip().lower()
            if key in self.options:
                value=str(value).strip().lower()
                self.out.append((key, value))
        return self

    def hexdigest(self):
        hash_ = repr(self.out) if self.out else ""
        if self._pre:
            hash_ = f"{self._pre}{hash_}"
        self.info(f"hash = {repr(hash_)}")
        return hash_


api = Api(
    app,
    prefix='/api',
    doc='/api/doc',
    version=f"v{version}",
    title=title,
    description=description,
)

CORS(app, resources={r'/*': {'origins': '*'}})



@app.after_request
def add_header(response):
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Cache-Control"] = 'public, max-age=0'
    return response



@app.before_request
def before_request_func():
    if request.path.startswith('/api/doc'):
        if request.args.get('url'):
            return redirect('/api/doc')



@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith('/api/'):
        return jsonify(
            code=e.code,
            name=e.name,
            description=e.description
        ), 404
    return redirect('/api/doc')



@app.route('/')
def index():
    return redirect('/api/doc')



coinpairs_ns = api.namespace('coinpairs',
                             description='Coinpairs related operations')



@coinpairs_ns.route('/')
class CoinPairsList(Resource):

    @api.doc(produces=['application/json', 'text/plain'])
    def get(self):
        """Shows a list of all supported coinpairs"""

        accept = request.headers.get('Accept', 'text/plain')
        
        if 'text/plain' in accept:
            text = tabulate(
                list([ (str(x), str(x.from_), str(x.to_), x.description
                        ) for x in AllCoinPairs]),
                headers=['Name', 'From', 'To', 'Description'],
                tablefmt="simple",
                stralign="left",
                numalign="right"
            )
            response = make_response(text, 200)
            response.mimetype = "text/plain"
            return response
        else:
            return list([{'name': str(x),
                          'from': str(x.from_),
                          'to': str(x.to_),
                          'description': x.description}
                          for x in AllCoinPairs])

coinpair_value_get = reqparse.RequestParser()
coinpair_value_get.add_argument(
    'coinpair',
    choices = all_coinpairs,
    type = str,
    help = 'Coinpair symbols')

bad_coinpair_choice = (400, 'Bad coinpair choice')
coinpair_value_not_found = (404, 'Coinpair value not found')

@coinpairs_ns.route('/get_value')
@coinpairs_ns.response(200, 'Success!')
@coinpairs_ns.response(*bad_coinpair_choice)
@coinpairs_ns.response(*coinpair_value_not_found)
class CoinPairValue(Resource):

    @coinpairs_ns.expect(coinpair_value_get)
    @cache.cached(
        timeout=5,
        query_string=True,
        hash_method=HashMethod(
            'coinpair',
            pre="get_coinpair_value",
            #info=lambda x: app.logger.info(f"Cache: {x}")
        )
    )
    def get(self):
        """Get the price of a specific coinpair"""

        args = coinpair_value_get.parse_args()
        coinpair = args['coinpair']

        if coinpair not in all_coinpairs:
            abort(*bad_coinpair_choice)

        detail = {}
        value = get_price(
            coinpairs=coinpair,
            detail=detail,
            serializable=True,
            ignore_zero_weighing=True)

        if isinstance(value, dict):
            value = dict([(str(k), float(v)) for (k, v) in value.items()])

        if isinstance(value, Decimal):
            value = float(value)

        sources_count = {}
        sources_count_ok = {}
        for p in detail.get('prices', []):
            sub_coinpair = p.get('coinpair', 'unknown')
            sources_count[sub_coinpair] = sources_count.get(
                sub_coinpair, 0) + 1
            if p.get('ok'):
                sources_count_ok[sub_coinpair] = sources_count_ok.get(
                    sub_coinpair, 0) + 1
            else:
                source = p.get('description', 'unknown')
                error = p.get('error', 'unknown')
                if coinpair==sub_coinpair:
                    app.logger.warning(f"{coinpair} --> {source} {error}")
                else:
                    app.logger.warning(
                        f"{sub_coinpair} for {coinpair} --> {source} {error}")

        for sub_coinpair, p in detail.get('values', {}).items():
            error = p.get('error')
            if error:
                if coinpair==sub_coinpair:
                    app.logger.warning(f"{coinpair} --> {error}")
                else:
                    app.logger.warning(
                        f"{sub_coinpair} for {coinpair} --> {error}")

        if sources_count:
            sources_count_str = ', '.join(
                [ f"{k}: {sources_count_ok[k]} of {v}"
                 for (k, v) in sources_count.items()])
            if len(sources_count)>1:
                app.logger.info(
                    f"Sources count for {coinpair}: {sources_count_str}")
            else:
                app.logger.info(f"Sources count for {sources_count_str}")

        if value:
            app.logger.info(f"Value for {coinpair}: {value}")
        else:
            app.logger.error(f"Not value for {coinpair}")
            abort(*coinpair_value_not_found)
            

        out = {}
        out['required_coinpair'] = coinpair 
        out['value'] = value
        out['detail'] = detail

        return out


class DictWithAlternativeJson(dict):

    _json = ""
    _serializable_dict = {}

    @property
    def json(self):
        if not self._json:
            self._json = dumps(self, indent=2)
        return self._json
    
    @json.setter
    def json(self, value):
        if isinstance(value, dict):
            self._serializable_dict = value
            value = dumps(value, indent=2)
        elif not isinstance(value, str):
            raise ValueError("Invalid type for JSON serialization")
        else:
            self._serializable_dict = loads(value)
        self._json = value

    @property
    def table(self):
        return tabulate(self.items(), tablefmt="plain",
                        stralign="left", numalign="right")

    @property
    def serializable_dict(self):
        return self._serializable_dict

    def __str__(self):
        return self.table


def get_set_of_prices(*args, detail: dict = {}):
        
        if not args:
            raise ValueError("No arguments provided")
        
        if len(args)==1:
            if isinstance(args[0], (list, tuple)):
                args = list(args[0])
            else:
                args = [args[0]]
        args = [str(x).strip() for x in args if str(x).strip()]

        if not args:
            raise ValueError("No arguments provided")
        
        wildcard = ','.join(args)
        
        coinpairs = get_coin_pairs(wildcard)

        if not coinpairs:
            raise ValueError("No coinpairs provided")

        values = get_price(
            coinpairs=coinpairs,
            detail=detail,
            serializable=True,
            ignore_zero_weighing=True)

        if values is None:
            values = {}

        if isinstance(values, Decimal):
            values = {coinpairs[0]: values}

        for cp in coinpairs:
            if cp not in values:
                values[cp] = None

        out = DictWithAlternativeJson(values)
        out.json = {
            'values': dict([(str(k),None if v is None else float(v)
                             ) for (k,v) in values.items()]),
            'detail': detail
        }

        return out


coinpairs_values_get = reqparse.RequestParser()
coinpairs_values_get.add_argument(
    'coinpairs',
    type = lambda s: get_coin_pairs(wildcard=s),
    help = 'Set of coinpairs symbols')
bad_coinpairs_set = (400, 'Bad set of coinpairs symbols')
max_coinpairs_reached = (403, 
    f'Forbidden, max number of pairs reached ({max_coinpair_limit})')
coinpairs_value_not_found = (404, 'Non coinpairs value found')

@coinpairs_ns.route('/get_values')
@coinpairs_ns.response(200, 'Success!')
@coinpairs_ns.response(*bad_coinpairs_set)
@coinpairs_ns.response(*max_coinpairs_reached)
@coinpairs_ns.response(*coinpairs_value_not_found)
class CoinPairsValue(Resource):

    @coinpairs_ns.expect(coinpairs_values_get)
    @cache.cached(
        timeout=10,
        query_string=True,
        hash_method=HashMethod(
            'coinpairs',
            pre="get_coinpairs_value",
        )
    )
    def get(self):
        """
        Get the price of a specific set of coinpairs
        
        The __coinpairs__ parameter is required.
        It represents the pairs you want to get the price for.
        
        It supports:

        * A single parameter like __BTC/USD__
        * Multiple parameters in a list, e.g.: __BTC/USD,USD/ARS__
        * Accepts wildcards, e.g., __*/ARS__
        * Or combinations, e.g.: __BTC/USD,*/ARS__

        """

        args = coinpairs_values_get.parse_args()
        coinpairs = args['coinpairs']

        if not coinpairs:
            abort(*bad_coinpairs_set)

        if len(coinpairs)>max_coinpair_limit:
            abort(*max_coinpairs_reached)

        detail = {}
       
        out = get_set_of_prices(coinpairs, detail=detail)

        self._extra_log(coinpairs, detail)

        if not out:
            abort(*coinpairs_value_not_found)       
        
        return out.serializable_dict

    @staticmethod
    def _extra_log(coinpairs, detail):
        warn, info  = app.logger.warning, app.logger.info
        values = detail.get('values', {})
        prices = detail.get('prices', {})
        for coinpair in map(str, coinpairs):
            sub_coinpairs = values.get(coinpair, {}).get(
                "requirements", [coinpair])
            sources_count = {}
            sources_count_ok = {}
            for p in prices:
                sub_coinpair = p.get('coinpair', 'unknown')
                if sub_coinpair in sub_coinpairs:
                    sources_count[sub_coinpair] = sources_count.get(
                        sub_coinpair, 0) + 1
                    if p.get('ok'):
                        sources_count_ok[sub_coinpair] = sources_count_ok.get(
                            sub_coinpair, 0) + 1
                    else:
                        source = p.get('description', 'unknown')
                        error = p.get('error', 'unknown')
                        str_value = f"{source} {error}"
                        if coinpair==sub_coinpair:
                            str_title = coinpair
                        else:
                            str_title = f"{sub_coinpair} for {coinpair}"
                        warn(f"{str_title} --> {str_value}")
            if len(sub_coinpairs)>1:
                pass
            if sources_count:
                sources_count_str = ', '.join([
                    f"{k}: {sources_count_ok.get(k, 'N/A')} of {v}"
                    for (k, v) in sources_count.items()])
                if len(sub_coinpairs)>1:
                    str_title = f"Sources count for {coinpair} are"
                else:
                    str_title = "Sources count for"
                info(f"{str_title} {sources_count_str}")



@api.route('/info')
class Info(Resource):

    def get(self):
        """Shows API info related"""
        return {
            'name:': title,
            'version' : version,
            'use_redis': use_redis,
            'max_coinpair_limit': max_coinpair_limit
        }



def main(host='0.0.0.0', port=7989, debug=False):
    #default_logger_level = app.logger.level
    app.logger.setLevel(1)
    app.logger.info(f"{title} (v{version})")
    app.logger.info(f"service at {host}:{port}")
    #app.logger.setLevel(default_logger_level)
    app.run(debug=debug, host=host, port=port)


@command()
@option('-a', '--addr', 'host', type=str,
        default='0.0.0.0', help='Server host addr.')
@option('-p', '--port', 'port', type=int,
        default=7989, help='Server port.')
def server_cli(host, port):
    """MoC prices source API Rest webservice"""
    main(host=host, port=port)



if __name__ == '__main__':
    main(debug=True)
