from engine_base import Base, BTC_COP
from decimal import Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "buda.com"
    _uri         = "https://www.buda.com/api/v2/markets/BTC-COP/ticker"
    _coinpair    = BTC_COP
    
    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _map(self, data):
        return {
            'price': (Decimal(data['ticker']['min_ask'][0]) + Decimal(data['ticker']['max_bid'][0])) / Decimal('2'),
            'volume': data['ticker']['volume'][0]
        }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
