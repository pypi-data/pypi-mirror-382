import sys, json, datetime
from os.path import dirname, abspath
from decimal import Decimal

base_dir = dirname(abspath(__file__))

with open(base_dir + "/version.txt", "r") as file_:
    version = file_.read().split()[0]
__version__ = version

bkpath   = sys.path[:]
sys.path.insert(0, dirname(base_dir))

from moc_prices_source.engines        import get_coinpair_list, get_engines_names, get_prices, session_storage
from moc_prices_source.computed_pairs import computed_pairs
from moc_prices_source.weighing       import weighing, weighted_median, median, mean
from moc_prices_source.coins          import *

sys.path = bkpath



ALL = CoinPairs



def get_price(
    coinpairs            = None,
    engines_names        = None,
    detail               = {},
    weighing             = weighing,
    serializable         = False,
    ignore_zero_weighing = True):

    start_time = datetime.datetime.now()

    requested = coinpairs

    if coinpairs:

        if not isinstance(coinpairs, list):
            coinpairs = [coinpairs]

        requested = coinpairs

        new_coinpairs = []
        for c in coinpairs:
            if c in computed_pairs:
                for r in computed_pairs[c]['requirements']:
                    new_coinpairs.append(r)
            elif c in ALL:
                new_coinpairs.append(c)
        coinpairs = list(set(new_coinpairs))

    if 'as_dict' in dir(weighing):
        weighing = weighing.as_dict
    else:
        for key, value in weighing.items():
            weighing[key] = Decimal(str(value))
    
    if ignore_zero_weighing:
        for key in list(weighing.keys()):
            if not weighing[key]:
                del weighing[key]

    if engines_names is None:
        engines_names = list(weighing.keys())

    prices = get_prices(
        coinpairs     = coinpairs,
        engines_names = engines_names)

    for value in prices:
        value['weighing'] = weighing.get(value['name'], Decimal('0.0'))

    detail['prices'] = prices

    coinpair_prices = {}
    for value in prices:
        value['percentual_weighing'] = None
        if value['ok']:
            if not value['coinpair'] in coinpair_prices:
                coinpair_prices[value['coinpair']] = {
                    'data': [],
                    'sum_weighing': Decimal('0.0')}
            coinpair_prices[value['coinpair']]['data'].append(value)
            coinpair_prices[value['coinpair']]['sum_weighing'] += value['weighing']

    for d in coinpair_prices.values():
        sum_weighing = d['sum_weighing']
        for v in d['data']:
            weighing = v['weighing']
            if not weighing:
                percentual_weighing = Decimal('0.0')
            elif not sum_weighing:
                percentual_weighing = Decimal('0.0')
            else:
                percentual_weighing = weighing / sum_weighing
            v['percentual_weighing'] = percentual_weighing

    for k, d in coinpair_prices.items():
        if not 'weighings' in d:
            d['weighings'] = []
        if not 'prices' in d:
            d['prices'] = []
        for v in d['data']:
            d['weighings'].append(v['percentual_weighing'])
            d['prices'].append(v['price'])
        del d['data']
        del d['sum_weighing']

        ok_sources_count = len(list(filter(bool, d['weighings'])))
        min_ok_sources_count = k.min_ok_sources_count

        d['median_price'] = median(d['prices'])
        d['mean_price'] = mean(d['prices'])
        if any (d['weighings']):
            d['weighted_median_price'] = weighted_median(d['prices'], d['weighings'])
        else:
            d['weighted_median_price'] = None

        d['ok_sources_count'] = ok_sources_count
        d['min_ok_sources_count'] = min_ok_sources_count
        d['ok'] = True
        d['error'] = ''
        d['ok_value'] = d['weighted_median_price']

        if ok_sources_count < min_ok_sources_count:
            d['ok'] = False
            d['error'] = f"Not enough price sources ({ok_sources_count} < {min_ok_sources_count})"
            d['ok_value'] = None

    if requested:
        for r in [r for r in requested if (
            (r in computed_pairs) and (not r in coinpair_prices)) ]:
            requirements = computed_pairs[r]['requirements']
            if set(requirements).issubset(set(coinpair_prices.keys())):
                coinpair_prices[r] = {}
                coinpair_prices[r]['ok'] = all([ coinpair_prices[q]['ok'] for q in requirements ])
                coinpair_prices[r]['requirements'] = requirements
                formula = computed_pairs[r]['formula']
                for k in ['median_price', 'mean_price', 'weighted_median_price']:
                    args = [ coinpair_prices[q][k] for q in requirements ]
                    try:
                        coinpair_prices[r][k] = formula(*args)
                    except:
                        coinpair_prices[r][k] = None
                coinpair_prices[r]['ok_value'] = (coinpair_prices[r]['weighted_median_price'] if 
                                                  coinpair_prices[r]['ok'] else None)

    detail['values'] = coinpair_prices

    out = {}

    for key, value in coinpair_prices.items():
        if requested:
            if key in requested:
                if value['weighted_median_price'] and value['ok']:
                    out[key] = value['weighted_median_price']
        else:
            if value['weighted_median_price'] and value['ok']:
                out[key] = value['weighted_median_price']

    if requested and len(requested)==1:
        if requested[0] in out:
            out = out[requested[0]]
        else:
            out = None

    if not(requested) and  len(out)==1:
        out = list(out.values())[0]

    detail['time'] = datetime.datetime.now() - start_time

    if serializable:
        detail['time'] = detail['time'].seconds + detail['time'].microseconds/1000000
        for p in prices:
            p['coinpair'] = str(p['coinpair'])
            if p['time']:
                p['time'] = p['time'].seconds + p['time'].microseconds/1000000
            p['timestamp'] = str(p['timestamp'])
            p['last_change_timestamp'] = str(p['last_change_timestamp'])
            if p['error']:
                p['error'] = str(p['error'])
            for k in ['price', 'weighing', 'percentual_weighing', 'volume']:
                if p[k]!=None:
                    p[k] = float(p[k])
        for d in coinpair_prices.values():
            for k in ['weighings', 'prices']:
                if k in d:
                    d[k] = [ float(x) for x in d[k] if d[k] ]
            for k in ['median_price', 'mean_price', 'weighted_median_price', 'ok_value']:
                if d[k]:
                    d[k] = float(d[k])
        for k in list(coinpair_prices.keys()):
            v = coinpair_prices[k]
            del coinpair_prices[k]
            coinpair_prices[str(k)] = v
            if 'requirements' in coinpair_prices[str(k)]:
                coinpair_prices[str(k)]['requirements'] = list(
                    map(str, coinpair_prices[str(k)]['requirements']))

    if not out:
        return None

    return out



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    print('Version: {}'.format(version))
    detail = {}
    output = get_price(ALL, detail=detail, serializable=True)
    print()
    print(json.dumps(detail, indent=4, sort_keys=True))
    print()
    print('output = {}'.format(repr(output)))
