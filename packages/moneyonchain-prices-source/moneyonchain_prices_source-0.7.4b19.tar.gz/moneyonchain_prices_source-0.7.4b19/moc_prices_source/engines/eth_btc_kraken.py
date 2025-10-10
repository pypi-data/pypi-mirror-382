from engine_base import Base, ETH_BTC


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Kraken"
    _uri         = "https://api.kraken.com/0/public/Ticker?pair=ETHBTC"
    _coinpair    = ETH_BTC

    def _map(self, data):
        return {
            'price':  data['result']['XETHXXBT']['c'][0],
            'volume': data['result']['XETHXXBT']['v'][1] }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
