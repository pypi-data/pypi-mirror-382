from engine_base import BaseWithFailover, BNB_USDT

base_uri = "https://{}/api/v3/ticker/24hr?symbol=BNBUSDT"

class Engine(BaseWithFailover):

    _name         = BaseWithFailover._name_from_file(__file__)
    _description  = "Binance"
    _uri          = base_uri.format("api.binance.com")
    _uri_failover = base_uri.format("moc-proxy-api-binance.moneyonchain.com")
    _coinpair     = BNB_USDT
    _max_time_without_price_change = 0 # zero means infinity

    def _map(self, data):
        return {
            'price':  data['lastPrice'],
            'volume': data['volume']}


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(f"URI = {repr(engine.uri)}")
    print()
    print(engine)
