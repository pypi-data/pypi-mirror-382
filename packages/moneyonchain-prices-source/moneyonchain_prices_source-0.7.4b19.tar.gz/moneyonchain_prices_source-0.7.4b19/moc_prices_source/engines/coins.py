from fnmatch import fnmatch as match


class Coin(object):

    def __init__(self, name: str, symbol: str, small_symbol=None):
        self._name = str(name).strip()
        self._symbol =str(symbol).strip().upper()
        self._small_symbol = str(small_symbol).strip() if small_symbol else None

    @property
    def name(self):
        return self._name

    @property
    def symbol(self):
        return self._symbol

    @property
    def small_symbol(self):
        return self._small_symbol

    def get_symbol(self):
        """ Get small symbol or symbol """
        return self.small_symbol or self.symbol

    @property
    def as_dict(self):
        return {
            'name':         self.name,
            'symbol':       self.symbol,
            'small_symbol': self.small_symbol,
        }

    def __str__(self):
        return self.symbol

    def __repr__(self):
        return "<{} Coin object>".format(self.name)

    def __eq__(self, other):
        return str(self).lower()==str(other).strip().lower()

    def __lt__(self, other):
        return str(self).lower()<str(other).strip().lower()

    def __hash__(self):
        return hash(str(self))


BTC = Coin('Bitcoin', 'btc', '₿')
USD = Coin('Dollar', 'usd', '$')
RIF = Coin('RIF Token', 'rif')
MOC = Coin('MOC Token', 'moc')
ETH = Coin('Ether', 'eth', '⟠')
USDT = Coin('Tether', 'usdt', '₮')
BNB = Coin('Binance Coin', 'bnb', 'Ƀ')
ARS = Coin('Peso Argentino', 'ars', '$')
MXN = Coin('Peso Mexicano', 'mxn', '$')
COP = Coin('Peso Colombiano','cop', '$')
GAS = Coin('Gas', 'gas')
BPRO = Coin('Bpro', 'bpro')
DOC = Coin('DOC Token', 'doc')


Coins = [ c for c in locals().values() if isinstance(c, Coin) ]



def get_coin(value):
    value = str(value).strip().lower()
    try:
        return dict([ (str(c.name).strip().lower(), c) for c in Coins])[value]
    except KeyError:
        return dict([ (str(c).strip().lower(), c) for c in Coins])[value]
        


class CoinPair(object):

    def __init__(self,
                 from_: Coin, to_: Coin, variant=None, description=None,
                 min_ok_sources_count = 0):
        self._from = from_
        self._to = to_
        self._variant = str(variant) if variant else None
        self._description = str(description) if description else None
        self._min_ok_sources_count = int(min_ok_sources_count) if min_ok_sources_count else 0

    @property
    def min_ok_sources_count(self):
        return self._min_ok_sources_count
    
    @property
    def description(self):
        return self._description
    
    @property
    def variant(self):
        return self._variant

    @property
    def from_(self):
        return self._from

    @property
    def to_(self):
        return self._to

    @property
    def long_name(self):
        return f"{self} (from {self.from_.name} to {self.to_.name})"
    
    @property
    def as_dict(self):
        return {
            'from':    self.from_,
            'to':      self.to_,
            'variant': self.variant
        }

    def __str__(self):
        if self.variant:
            return '{}/{}({})'.format(self.from_.symbol, self.to_.symbol, self.variant)
        return '{}/{}'.format(self.from_.symbol, self.to_.symbol)

    def __repr__(self):
        return "<{} Coin Pair object>".format(str(self))

    def __eq__(self, other):
        return str(self).lower()==str(other).strip().lower()

    def __lt__(self, other):
        return str(self).lower()<str(other).strip().lower()

    def __hash__(self):
        return hash(str(self))


# BNB/USD
BNB_USD = CoinPair(BNB, USD)

# BNB/USDT
BNB_USDT = CoinPair(BNB, USDT)

# BPRO/ARS
BPRO_ARS = CoinPair(BPRO, ARS)

# BPRO/BTC
BPRO_BTC = CoinPair(BPRO, BTC)

# BPRO/COP
BPRO_COP = CoinPair(BPRO, COP)

# BPRO/USD
BPRO_USD = CoinPair(BPRO, USD, description="Offchain")

# DOC/USD
DOC_USD = CoinPair(DOC, USD, description="Pegged 1:1 to USD")

# BTC/ARS
BTC_ARS = CoinPair(BTC, ARS, min_ok_sources_count=3)

# BTC/COP
BTC_COP = CoinPair(BTC, COP, min_ok_sources_count=2)

# BTC/USD
BTC_USD = CoinPair(BTC, USD)
BTC_USD_OCH = CoinPair(BTC, USD, "och", "Obtained from the blockchain")

# BTC/USDT
BTC_USDT = CoinPair(BTC, USDT)

# ETH/BTC
ETH_BTC = CoinPair(ETH, BTC)

# ETH/USD
ETH_USD = CoinPair(ETH, USD)
ETH_USD_B = CoinPair(ETH, USD, "B", "Passing through Bitcoin")

# GAS/BTC Rootstock gas price from nodes
GAS_BTC = CoinPair(GAS, BTC, description="Rootstock gas price from nodes")

# MOC/BPRO
MOC_BPRO = CoinPair(MOC, BPRO)

# MOC/BTC
MOC_BTC = CoinPair(MOC, BTC)
MOC_BTC_SOV = CoinPair(MOC, BTC, "Sovryn")

# MOC/USD
MOC_USD = CoinPair(MOC, USD, description="Default option, weighted median")
MOC_USD_OKU = CoinPair(MOC, USD, "Oku")
MOC_USD_SOV = CoinPair(MOC, USD, "Sovryn")
MOC_USD_WM = CoinPair(MOC, USD, "WM", "Weighted median")

# RIF/BTC
RIF_BTC = CoinPair(RIF, BTC)
RIF_BTC_MP1P = CoinPair(RIF, BTC, "mp1%", "To move the price 1 percent")

# RIF/USD
RIF_USD = CoinPair(RIF, USD, description="Leave this as legacy")
RIF_USD_B = CoinPair(RIF, USD, "B", "Passing through Bitcoin")
RIF_USD_T = CoinPair(RIF, USD, "T", "Passing through Tether")
RIF_USD_TB = CoinPair(RIF, USD, "TB", "Passing through Tether & Bitcoin")
RIF_USD_TBMA = CoinPair(RIF, USD, "TBMA", "Passing through Tether & Bitcoin, using [WDAP](fundamentals/wdap.md)")
RIF_USD_TMA = CoinPair(RIF, USD, "TMA", "Passing through Tether, using [WDAP](fundamentals/wdap.md)")
RIF_USD_WMTB = CoinPair(RIF, USD, "WMTB", "Passing through Tether & Bitcoin usinng weighted median")

# RIF/USDT
RIF_USDT = CoinPair(RIF, USDT)
RIF_USDT_MA = CoinPair(RIF, USDT, "MA", "Using [WDAP](fundamentals/wdap.md)")
RIF_USDT_MA2 = CoinPair(RIF, USDT, "MA2")
RIF_USDT_MA3 = CoinPair(RIF, USDT, "MA3")
RIF_USDT_MP1P = CoinPair(RIF, USDT, "mp1%", "To move the price 1 percent")

# USD/ARS
USD_ARS = CoinPair(USD, ARS, description="Free, from the news portals")
USD_ARS_CCB = CoinPair(USD, ARS, "CCB")
USD_ARS_CCL = CoinPair(USD, ARS, "CCL")

# USD/COP
USD_COP = CoinPair(USD, COP, description="Free, from the news portals")
USD_COP_CCB = CoinPair(USD, COP, "CCB")

# USD/MXN
USD_MXN = CoinPair(USD, MXN)

# USDT/USD
USDT_USD = CoinPair(USDT, USD)
USDT_USD_B = CoinPair(USDT, USD, "B", "Passing through Bitcoin")


CoinPairs = [ c for c in locals().values() if isinstance(c, CoinPair) ]



def get_coin_pair(value):
    value = str(value).strip().lower()
    return dict([ (str(c).strip().lower(), c) for c in CoinPairs ])[value]


def get_coin_pairs(
        wildcard: str = "*",
        coinpairs_base: list = None
        ) -> list:
    """
    Get all coin pairs that match the wildcard.
    """
    if coinpairs_base is None:
        coinpairs_base =  CoinPairs
    wildcards_base = str(wildcard).lower().replace(" ", ",").split(",")
    wildcards = list(set([w for w in wildcards_base if w]))
    coinpairs = []
    for w in wildcards:
        f = filter(lambda i: match(str(i).lower(), w), coinpairs_base)
        f = list(set(list(f)))
        coinpairs.extend(f)
    coinpairs = list(set(coinpairs))
    return coinpairs


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
        if c.variant:
            print(f'    {c} (from {c.from_.name} to {c.to_.name}, {c.variant})')
        else:    
            print(f'    {c} (from {c.from_.name} to {c.to_.name})')
