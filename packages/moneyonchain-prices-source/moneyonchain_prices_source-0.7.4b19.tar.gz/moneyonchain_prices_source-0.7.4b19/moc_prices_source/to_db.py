import sys, datetime, json
from os.path import dirname, abspath
from time import sleep
from tabulate import tabulate
from sys import stderr
from decimal import Decimal

bkpath = sys.path[:]
base_dir = dirname(abspath(__file__))
sys.path.insert(0, dirname(base_dir))

from moc_prices_source import get_price
from moc_prices_source import ALL, get_coin_pairs
from moc_prices_source.cli import command, option, cli
from moc_prices_source.database import make_db_conn
from moc_prices_source.my_logging import make_log, INFO, DEBUG, VERBOSE
from moc_prices_source.redis_conn import get_redis, redis_conf_file

sys.path = bkpath
app_name = 'moc_prices_source'



class OutputClose(Exception):
    pass



class OutputBase(object):

    def __init__(self, name,
                 verbose  = print,
                 critical = lambda m: print(m, file=stderr),
                 info = lambda m: print(m, file=stderr)):
        self._verbose  = verbose
        self._critical = critical
        self._info = info
        self._name = name
        self._open = False
        self._start()
        self._open = True

    @property
    def name(self):
        return self._name
    
    def __bool__(self):
        return self._open

    def __call__(self, value):
        if self:
            return self._call(value)
        else:
            raise OutputClose()

    def close(self):
        if self:
            self._end()
            self._open = False

    def __del__(self):
        self.close()

    def _start(self):
        pass

    def _call(self, value):
        pass

    def _end(self):
        pass



class OutputDB(OutputBase):

    def __init__(self, name,
                 verbose  = print,
                 critical = lambda m: print(m, file=stderr),
                 info = lambda m: print(m, file=stderr),
                 only_redis = False):
        
        OutputBase.__init__(self, name,
                 verbose  = verbose,
                 critical = critical,
                 info = info)
        
        self._only_redis = only_redis

        self._database = None
        if not only_redis:
            try:
                self._database = make_db_conn()
            except Exception as e:
                exit(1)
               
        self._redis = get_redis()

        if only_redis and self._redis is None:
            print(f'Error, Redis not enabled in config (File: {redis_conf_file})',
                  file=stderr)
            exit(1)


    def _call(self, value):
        data = {}
        for timestamp, name, v in value:
            if not timestamp in data:
                data[timestamp] = {}
            data[timestamp][name] = v
        timestamps = list(data.keys())
        timestamps.sort(key=lambda x: x.timestamp())
        for timestamp in timestamps:
            kargs = {
                'measurement': self.name,
                'time_':       timestamp,
                'fields':      data[timestamp]
            }
            if self._database is not None:
                self._database.write(**kargs)
                into = f"{kargs['measurement']}@{kargs['time_'].strftime('%Y-%m-%dT%H:%M:%S')}"
                self._info(
                    f"Insert into {into} {len(kargs['fields'])} fileds.")
            if self._redis is not None:
                for (k, v) in kargs['fields'].items():
                    for (key, value) in [
                            (f"{self.name}/{k}", v),
                            (f"{self.name}/{k}/timestamp", timestamp)]:
                        if isinstance(value, Decimal):
                            value = float(value)
                        if isinstance(value, datetime.datetime):
                            value = datetime.datetime.timestamp(value)
                        elif value!=None and not(isinstance(
                                value, (int, bool, float))):
                            value = str(value)
                        value = json.dumps(value)
                        self._redis.set(key, value)
                into = f"redis@{kargs['time_'].strftime('%Y-%m-%dT%H:%M:%S')}"
                self._info(
                    f"Insert into {into} {len(kargs['fields'])*2} fileds.")



def get_values(log,
               coinpairs = ALL,
               ignore_zero_weighing = False):

    # Get prices
    d = {}
    get_price(
        coinpairs,
        ignore_zero_weighing = ignore_zero_weighing,
        detail=d)

    # Log errors
    sources_count = {}
    sources_count_ok = {}
    for e in d['prices']:
        coinpair = e['coinpair']
        weighing = e['weighing']
        if weighing:
            sources_count[coinpair] = sources_count.get(coinpair, 0) + 1
            sources_count_ok[coinpair] = sources_count_ok.get(coinpair, 0)
        if e['ok']:
            if weighing:
                sources_count_ok[coinpair] += 1
        else:
            exchange = e['description']
            error    = e['error']
            log.warning(f"{coinpair} --> {exchange} {error}")
    for coinpair, count in sources_count.items():
        if sources_count_ok[coinpair]!=count:
            log.warning(f"Sources count for {coinpair}: {sources_count_ok[coinpair]} of {count}")
    data = []

    for p in d['prices']:
        timestamp = p['timestamp'] if p['timestamp'] else datetime.datetime.now().replace(microsecond=0)
        coinpair =  p['coinpair']
        name =      p['description']
        price =     p['price']
        weighing =  None if p['percentual_weighing'] is None else float(p['percentual_weighing'])
        age =       None if p['age'] is None else int(p['age'])
        error =     None if p['error'] is None else str(p['error'])
        row = {
            'timestamp':            timestamp,
            'coinpair':             coinpair,
            'name':                 name,
            'price':                price,
            'percentual_weighing':  weighing,
            'age': age,
            'error': error
        }
        log.verbose(f'Exchange {name} {coinpair} value: {price}')
        data.append(row)

    for coinpair, v in d['values'].items():
        median_price =          v['median_price']
        mean_price =            v['mean_price']
        weighted_median_price = v['weighted_median_price']
        row = {
            'timestamp': datetime.datetime.now().replace(microsecond=0),
            'coinpair': coinpair,
            'median_price': median_price,
            'mean_price': mean_price,
            'weighted_median_price': weighted_median_price
        }

        for key in ['ok_sources_count',
                    'min_ok_sources_count',
                    'ok',
                    'error',
                    'ok_value']:
            if key in v:
                row[key]=v[key]

        if 'ok' in v:
            row['int_ok'] = 1 if v['ok'] else 0

        if coinpair in sources_count:
            row['sources_count'] = sources_count[coinpair]

        log.verbose(f'{coinpair} weighted:{weighted_median_price}, median;{median_price}, mean:{mean_price}')
        data.append(row)

    out = []

    for d in data:

        timestamp = d['timestamp']

        pre_name = str(d['coinpair']).split('/')
        if 'name' in d:
            pre_name += d['name'].split()
        pre_name += ['']
        pre_name = '_'.join(pre_name)

        for k in [k for k in d.keys() if k not in ['name', 'coinpair', 'timestamp']]:
            row = [timestamp, pre_name + k, d[k]] 
            out.append(row)

    out.sort(key=lambda x: x[0].timestamp())
    return out



@command()
@option('-v', '--verbose', 'verbose', count=True,
    help='Verbose mode.')
@option('-f', '--frequency', 'frequency', type=int, default=5,
    help='Loop delay in seconds.')
@option('-i', '--interval', 'interval', type=int, default=0,
    help='How long the program runs (in minutes, 0=∞).')
@option('-n', '--name', 'name', type=str, default=app_name,
    help=f"Time series name (default={repr(app_name)}).")
@option('-z', '--ignore-zero-weighing', 'ignore_zero_weighing', is_flag=True,
        help='Ignore sources with zero weighing.')
@option('-r', '--only-redis', 'only_redis', is_flag=True,
        help='Use only redis database.')
@cli.argument('coinpairs_filter', required=False)
def cli_values_to_db(
    frequency,
    verbose = 0,
    interval = 0,
    name = app_name,
    coinpairs_filter = None,
    ignore_zero_weighing = False,
    only_redis = False):
    """\b
Description:
    CLI-type tool that save the data obtained by
    the `moc_price_source` library into a InfluxDB
    and/or RedisDB.
\n\b
COINPAIRS_FILTER:
    Is a display pairs filter that accepts wildcards.
    Example: "btc*"
    Default value: "*" (all available pairs)
"""
    
    if coinpairs_filter:
        coinpairs = get_coin_pairs(coinpairs_filter)
    else:
        coinpairs = ALL
    if not coinpairs:
        print(
            f"The {repr(coinpairs_filter)} filter did not return any results.",
            file=stderr)
        return 1

    # Logger
    if verbose==0:
        level = INFO
    elif verbose==1:
        level = VERBOSE
    elif verbose>1:
        level = DEBUG
    log = make_log(app_name, level = level)
    log.info(f'Starts (frequency {frequency}s, time series {repr(name)})')
    if len(coinpairs)>3:
        log.info(f'Coinpairs count: {len(coinpairs)}')
    else:
        log.info(f"Coinpairs: {', '.join([str(c) for c in coinpairs])}")

    output = OutputDB(name,
                      verbose=log.verbose,
                      critical=log.critical,
                      info=log.info,
                      only_redis=only_redis)

    start_time = datetime.datetime.now()

    def condition():
        if not interval:
            return True
        until_now = datetime.datetime.now() - start_time
        return until_now <= datetime.timedelta(minutes=interval)

    try:
        while condition():
            output(get_values(log, coinpairs,
                              ignore_zero_weighing=ignore_zero_weighing))
            log.info(f'Wait {frequency}s ...')
            sleep(frequency)
    except KeyboardInterrupt:
        log.verbose('Keyboard interrupt!')
        print()
        print('Aborted!')
        print()

    if not condition():
        log.info(f'Ends (interval {interval}m)')        



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    log = make_log(app_name, level = INFO)
    values = get_values(log)
    print()
    print(tabulate(values, headers=['timestamp', 'key', 'value']))
    print()