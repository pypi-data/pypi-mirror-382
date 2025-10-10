import datetime, requests, sys
from os.path import dirname, abspath
from json import load, dumps, loads
from json.decoder import JSONDecodeError
from sys import stderr
from statistics import median, mean
from tabulate import tabulate
from decimal import Decimal
from os import environ

bkpath   = sys.path[:]
base_dir = dirname(abspath(__file__))
sys.path.insert(0, dirname(base_dir))

from moc_prices_source.conf import get

sys.path = bkpath

env_pre = 'MOC_PRICES_SOURCE'

on_remote_differences_options = ['halt', 'error', 'remote', 'local']

enabled = None
url = None
refresh_time_in_minutes = 60
on_remote_differences = on_remote_differences_options[0]
envs = {}

def call_back(options):

    enabled = None if not 'enabled' in options else options['enabled'] 
    if not(isinstance(enabled, bool) or enabled==None):
        raise ValueError('enabled must be bool or null')
    
    url = None if not 'url' in options else options['url'] 
    if not(isinstance(url, str) or url==None):
        raise ValueError('url must be str or null')

    refresh_time_in_minutes = 60 if not 'refresh_time_in_minutes' in options else options['refresh_time_in_minutes']
    if not(isinstance(refresh_time_in_minutes, int)):
        raise ValueError('refresh_time_in_minutes must be integer')
    if refresh_time_in_minutes<1:
        raise ValueError('refresh_time_in_minutes must be < 1')

    on_remote_differences = on_remote_differences_options[0] if not 'on_remote_differences' in options else options['on_remote_differences']
    if not(isinstance(on_remote_differences, str)):
        raise ValueError('on_remote_differences must be str')
    on_remote_differences = on_remote_differences.lower().strip()
    if on_remote_differences not in on_remote_differences_options:
        raise ValueError('on_remote_differences must be ' + ', '.join(map(repr, on_remote_differences_options[:-1])) + ' or ' + repr(on_remote_differences_options[-1]))

    return {
        'url': url,
        'refresh_time_in_minutes': refresh_time_in_minutes,
        'on_remote_differences': on_remote_differences
    }

kargs = dict(
    out          = locals(),
    call_back    = call_back,
    files        = ['remote_weighing.json', 'remote_weighing_default.json'],
    env_pre      = env_pre,
    dir_         = '/data/',
    copy_to_home = False,
    places       = dirname(abspath(__file__)))

get(**kargs)


filename = dirname(abspath(__file__)) + '/data/weighing.json'


class WeighingException(Exception):
    pass


def get_json_file():

    def config_error(e, source, s="Config file error\nLocation: {}\n{}"):
        print(s.format(source, e), file=stderr)
        exit(1)

    def validate_json_data(data):       
        if not isinstance(data, dict):
            return False
        for key, value in data.items():
            if isinstance(value, int):
                data[key]=float(value)
        for key, value in data.items():
            if not isinstance(key, str):
                return False
            if not isinstance(value, float):
                return False
        return True

    try:
        with open(filename) as json_file:
            data = load(json_file)
    except JSONDecodeError as e:
        config_error(e, filename)
    except FileNotFoundError as e:
        config_error('File not found!', filename)

    if not validate_json_data(data):
        str_err_map = "Bad mapping, has to be a dictionary with string keys and float values"
        config_error(str_err_map, filename)
    
    if enabled and  url and not(on_remote_differences=='local') :
        try:
            url_data = validate_json_data(requests.get(url).json())
        except:
            url_data = None
        if url_data and url_data!=data:
            if on_remote_differences=='error':
                raise WeighingException
            if on_remote_differences=='halt':
                print("Error: differences between local and remote weighing", file=stderr)
                exit(1)
            if on_remote_differences=='remote':
                data = url_data

    env = env_pre + "_WEIGHING_OVERRIDE"
    override_raw = environ.get(env, None)
    if override_raw:
        str_error = "Env var {} error: {}"
        try:
            override = loads(override_raw)
        except JSONDecodeError as e:
            config_error(e, env, str_error)
        if not validate_json_data(override):
            str_err_map = "Bad mapping, has to be a dictionary with string keys and float values"
            config_error(str_err_map, env, str_error)

        data = override

    return data



class Weighing(object):

    def __init__(self, refresh_time=datetime.timedelta(minutes=refresh_time_in_minutes)):
        self._data = {}
        self._last_load = None
        self._refresh_time = refresh_time
        self._load()

    def _load(self):

        if ((self._last_load is None) or (
            (datetime.datetime.now() - self._last_load) > self._refresh_time)):

            data = get_json_file()

            if isinstance(data, dict):
                ok = True
                try:
                    for key, value in data.items():
                        data[key] = Decimal(str(value))
                except:
                    ok = False

                if ok:
                    for key, value in data.items():
                        self._data[key] = value
                    self._last_load = datetime.datetime.now()

    @property
    def as_dict(self):
        self._load()
        return dict(self._data)

    @property
    def as_json(self):
        self._load()
        return dumps(dict([(k, float(v)) for k, v in self._data.items()]), indent=4)

    @property
    def names(self):
        return list(self.as_dict.keys())

    def __call__(self, name):
        return  self.as_dict.get(name, Decimal('0.0'))

    @property
    def last_load(self):
        return self._last_load

    @property
    def refresh_time(self):
        return self._refresh_time

    def __str__(self):
        return tabulate(list(self.as_dict.items()),
            headers=['Engine', 'Weigh'])



weighing = Weighing()



def weighted_median(values, weights):

    if not all(weights):
        non_zero = [(v, w) for (v, w) in zip(values, weights) if w]
        values = [v for (v, w) in non_zero]
        weights = [w for (v, w) in non_zero]
   
    count = len(values)
    
    if 1==count:
        return values[0]
    
    idx = weighted_median_idx(values, weights)

    if (count % 2) != 0:
        return values[idx] 

    if count -1 == idx:
        idx -= 1
    
    a, b = values[idx], values[idx + 1]
    base = weights[idx] + weights[idx + 1]
    p, q = weights[idx]/base, weights[idx + 1]/base

    if isinstance(a, Decimal) and not isinstance(p, Decimal):
        p = Decimal(p)
    if isinstance(b, Decimal) and not isinstance(q, Decimal):
        q = Decimal(q)      
    
    return (a * p) + (b * q)


def weighted_median_idx(values, weights):
    '''
    Compute the weighted median of values list.
    The weighted median is computed as follows:

    1- sort both lists (values and weights) based on values.
    
    2- select the 0.5 point from the weights and return the corresponding
       values as results.
    
    e.g. values = [1, 3, 0] and weights=[0.1, 0.3, 0.6] assuming weights
    are probabilities.
    
    sorted values = [0, 1, 3] and corresponding sorted weights = [0.6, 0.1,
    0.3] the 0.5 point on weight corresponds to the first item which is 0.
    so the weighted median is 0.
    '''

    # convert the weights into probabilities
    sum_weights = sum(weights)
    weights = [w / sum_weights for w in weights]
    
    # sort values and weights based on values
    sorted_tuples = sorted(zip(values, weights, range(len(values))))

    # select the median point
    cumulative_probability = 0
    for i in range(len(sorted_tuples)):
        cumulative_probability += sorted_tuples[i][1]
        if cumulative_probability >= 0.5:
            return sorted_tuples[i][2]
    return sorted_tuples[-1][2]



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    print("Config file: {}".format(repr(filename)))
    print()
    print('weighing.as_dict = {}'.format(repr(weighing.as_dict)))
    print()
    print(weighing)
    print()
