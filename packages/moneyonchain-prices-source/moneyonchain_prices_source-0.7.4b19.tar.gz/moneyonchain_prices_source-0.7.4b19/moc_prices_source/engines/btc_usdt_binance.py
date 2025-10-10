from engine_base import BaseWithFailover, BTC_USDT, Decimal

base_uri = "https://{}/api/v3/ticker/bookTicker?symbol=BTCUSDT"

class Engine(BaseWithFailover):

    _name         = BaseWithFailover._name_from_file(__file__)
    _description  = "Binance"
    _uri          = base_uri.format("api.binance.com")
    _uri_failover = base_uri.format("moc-proxy-api-binance.moneyonchain.com")
    _coinpair     = BTC_USDT
    _max_time_without_price_change = 600 # 10m, zero means infinity

    def _map(self, data):
        return {
            'price': (Decimal(data['askPrice']) +
                      Decimal(data['bidPrice'])) / Decimal('2')
        }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(f"URI = {repr(engine.uri)}")
    print()
    print(engine)
    print()
    if engine.error:
        print()
        print(engine.error)
        print()
