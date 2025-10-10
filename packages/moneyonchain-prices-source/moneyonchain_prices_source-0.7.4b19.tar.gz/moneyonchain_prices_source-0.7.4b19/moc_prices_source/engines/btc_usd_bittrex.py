from engine_base import Base, BTC_USD


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Bittrex"
    _uri         = "https://api.bittrex.com/api/v1.1/public/getticker?market=USD-BTC"
    _coinpair    = BTC_USD

    def _map(self, data):
        return {
            'price':  data['result']['Last'],
            }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
