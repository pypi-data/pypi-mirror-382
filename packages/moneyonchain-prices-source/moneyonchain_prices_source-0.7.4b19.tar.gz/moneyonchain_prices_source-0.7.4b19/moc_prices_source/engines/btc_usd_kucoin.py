from engine_base import Base, BTC_USD


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Kucoin"
    _uri         = "https://api.kucoin.com/api/v1/market/stats?symbol=BTC-USDT"
    _coinpair    = BTC_USD

    def _map(self, data):
        return {
            'price':  data['data']['last'],
            'volume': data['data']['vol'] }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
