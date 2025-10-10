from engine_base import Base, RIF_BTC


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Kucoin"
    _uri         = "https://openapi-v2.kucoin.com/api/v1/market/orderbook/level1?symbol=RIF-BTC"
    _coinpair    = RIF_BTC
    _max_time_without_price_change = 0 # zero means infinity

    def _map(self, data):
        return {
            'price':  data['data']['price'],
            'volume': data['data']['size'] }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
