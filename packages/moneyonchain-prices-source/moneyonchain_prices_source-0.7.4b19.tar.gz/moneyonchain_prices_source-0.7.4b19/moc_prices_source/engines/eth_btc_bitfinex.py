from engine_base import Base, ETH_BTC


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Bitfinex"
    _uri         = "https://api-pub.bitfinex.com/v2/ticker/tETHBTC"
    _coinpair    = ETH_BTC

    def _map(self, data):
        return {
            'price':  data[6],
            'volume': data[7]}


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
