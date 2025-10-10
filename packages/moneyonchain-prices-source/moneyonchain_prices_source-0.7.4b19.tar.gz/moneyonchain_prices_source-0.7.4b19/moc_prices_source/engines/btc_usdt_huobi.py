from engine_base import Base, BTC_USDT, Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Huobi"
    _uri         = "https://api.huobi.pro/market/detail/merged?symbol=btcusdt"
    _coinpair    = BTC_USDT
    _max_time_without_price_change = 600 # 10m, zero means infinity

    def _map(self, data):
        data = data['tick']     
        return {
            'price': (Decimal(data['bid'][0]) +
                      Decimal(data['ask'][0])) / Decimal('2')
        }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
