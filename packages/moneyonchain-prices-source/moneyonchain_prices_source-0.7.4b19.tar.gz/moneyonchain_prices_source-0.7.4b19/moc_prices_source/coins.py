import sys
from os.path  import dirname, abspath

bkpath   = sys.path[:]
base_dir = dirname(abspath(__file__))
sys.path.insert(0, dirname(base_dir))

from moc_prices_source.engines.coins import *

sys.path = bkpath


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    print()
    print('Coins:')
    for c in Coins:
        if c.small_symbol:
            print(f'    {c.name} ({c.symbol} or {c.small_symbol})')
        else:
            print(f'    {c.name} ({c.symbol})')
    print()
    print('Coin pairs:')
    for c in CoinPairs:
        print(f'    {c} (from {c.from_.name} to {c.to_.name})')
