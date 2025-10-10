from engine_base import Base, USDT_USD, Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Bitstamp"
    _uri         = "https://www.bitstamp.net/api/v2/ticker/usdtusd/"
    _coinpair    = USDT_USD
    _max_time_without_price_change = 3600 # 1h, zero means infinity

    def _map(self, data):
        return {
            'price': (Decimal(data['ask']) + Decimal(data['bid'])) / Decimal('2'),
            'volume': data['volume']}


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
