from engine_base import Base, BTC_USDT, Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "KuCoin"
    _uri         = "https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=BTC-USDT"
    _coinpair    = BTC_USDT
    _max_time_without_price_change = 600 # 10m, zero means infinity

    def _map(self, data):
        data = data['data']        
        return {
            'price': (Decimal(data['bestAsk']) +
                      Decimal(data['bestBid'])) / Decimal('2')
        }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
