from engine_base import Base, BTC_USD


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "BitGO"
    _uri         = "https://www.bitgo.com/api/v1/market/latest"
    _coinpair    = BTC_USD

    def _map(self, data):
        return {
            'price':  data['latest']['currencies']['USD']['last'],
            'volume': data['latest']['currencies']['USD']['total_vol'],
            'timestamp': self._utcfromtimestamp(data['latest']['currencies']['USD']['timestamp']) }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
