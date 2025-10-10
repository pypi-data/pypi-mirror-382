from engine_base import Base, USDT_USD, Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Kraken"
    _uri         = "https://api.kraken.com/0/public/Ticker?pair=USDTUSD"
    _coinpair    = USDT_USD
    _max_time_without_price_change = 3600 # 1h, zero means infinity

    def _map(self, data):
        keys = list(data['result'].keys())
        if 1==len(keys):
            return {
                'price': (Decimal(data['result'][keys[0]]['a'][0]) +
                          Decimal(data['result'][keys[0]]['b'][0])
                          ) / Decimal('2'),
                'volume': data['result'][keys[0]]['v'][1] }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
