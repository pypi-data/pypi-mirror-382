from engine_base import Base, BTC_USDT, Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "OKX"
    _uri         = "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT"
    _coinpair    = BTC_USDT
    _max_time_without_price_change = 600 # 10m, zero means infinity

    def _map(self, data):
        data = data['data'][0]        
        return {
            'price': (Decimal(data['askPx']) +
                      Decimal(data['bidPx'])) / Decimal('2')
        }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
