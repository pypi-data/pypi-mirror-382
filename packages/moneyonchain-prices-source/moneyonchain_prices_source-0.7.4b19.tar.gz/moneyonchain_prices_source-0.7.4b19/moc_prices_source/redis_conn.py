import json, sys
from sys import stderr
from os.path import basename, dirname, abspath, expanduser
from json.decoder import JSONDecodeError
from redis import Redis
from time import sleep

bkpath   = sys.path[:]
base_dir = dirname(abspath(__file__))
sys.path.insert(0, dirname(base_dir))

from moc_prices_source.my_logging import make_log

sys.path = bkpath



log = make_log('RedisDB')

def get_redis_conf():
    app_dir  = dirname(abspath(__file__))
    app_name = basename(app_dir)
    redis_conf_files = [expanduser("~") + '/.' + app_name + '/redis.json',
                        expanduser("~") + '/.' + app_name + '/redis_default.json',
                        app_dir + '/data/redis.json',
                        app_dir + '/data/redis_default.json']
    redis_conf = {}
    for file_ in redis_conf_files:
        try:
            with open(file_, 'r') as f:
                redis_conf = json.load(f)
        except JSONDecodeError as e:
            print(f'Error in "{file_}", {str(e)}', file=stderr)
            exit(1)
        except Exception as e:
            redis_conf = {}
        if redis_conf:
            break
    redis_conf['file'] = file_
    connection_parameters = {}
    for key, type_ in [('host', str),
                       ('port', int),
                       ('db', int),
                       ('unix_socket_path', str)]:
        if key in redis_conf:
            try:
                connection_parameters[key] = type_(redis_conf[key])
            except Exception as e:
                print(f'Error in "{file_}", {str(e)}',
                      file=stderr)
                exit(1)
    redis_conf['connection_parameters'] = connection_parameters
    return redis_conf

redis_conf = get_redis_conf()

use_redis = redis_conf.get('enable', False)

redis_conf_file = redis_conf.get('file', 'unknown')

redis_conn_parameters = redis_conf.get('connection_parameters', {})

retry_count = redis_conf.get('retry_count', 0)
retry_delay = redis_conf.get('retry_delay', 3)

def get_redis(retry_count=retry_count, retry_delay=retry_delay, log=log):
    if not use_redis:
        return None
    redis = None
    for i in range(retry_count + 1):
        if i:
            log.info(f"Connecting retry in {retry_delay}s...")
            try:
                sleep(retry_delay)
            except KeyboardInterrupt as e:
                log.info('Aborted! (keyboard interrupt).')
                print(f"\nAborted!\n", file=stderr)
                exit(1)
            log.info(f"Connecting retry {i} of {retry_count}...")
        error = None
        try:
            redis = Redis(**redis_conn_parameters) if redis is None else redis
            redis.ping()
        except KeyboardInterrupt as e:
            if i:
                log.info('Aborted! (keyboard interrupt).')
            print(f"\nAborted!\n", file=stderr)
            exit(1)            
        except Exception as e:
            error = e
        if error is None:
            break
    if i and error is None:
        log.info(f"Connected to RedisDB.")    
    if error is not None:
        msg = f'Error in "{redis_conf_file}", {str(error)}'
        if i:
            log.error(msg)
        print(msg, file=stderr)
        exit(1)
    return redis



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    print()
    print(f"{redis_conf_file=}")
    print(f"{use_redis=}")
    print(f"{redis_conn_parameters=}")

