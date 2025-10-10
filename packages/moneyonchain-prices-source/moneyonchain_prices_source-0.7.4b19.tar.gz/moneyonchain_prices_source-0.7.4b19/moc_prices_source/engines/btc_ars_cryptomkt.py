from engine_base import Base, BTC_ARS
from decimal import Decimal

class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "cryptomkt.com"
    _uri         = "https://api.exchange.cryptomkt.com/api/3/public/ticker/BTCARS"
    _coinpair    = BTC_ARS
    
    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _map(self, data):
        return {
            'price': (Decimal(data['ask']) + Decimal(data['bid'])) / Decimal('2'),
            'volume': data['volume']
        }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
