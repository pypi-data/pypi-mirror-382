from engine_base import Base, BTC_USD


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Blockchain"
    _uri         = "https://blockchain.info/ticker"
    _coinpair    = BTC_USD

    def _map(self, data):
        return {
            'price':  data['USD']['last']
            }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
