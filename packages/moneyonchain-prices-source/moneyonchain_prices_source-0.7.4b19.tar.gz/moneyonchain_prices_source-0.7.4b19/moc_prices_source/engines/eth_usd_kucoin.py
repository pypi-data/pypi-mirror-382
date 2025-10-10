from engine_base import Base, ETH_USD


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Kucoin"
    _uri         = "https://api.kucoin.com/api/v1/market/stats?symbol=ETH-USDT"
    _coinpair    = ETH_USD

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
