from engine_base import Base, RIF_BTC


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Coinbene"
    _uri         = "https://openapi-exchange.coinbene.com/api/exchange/v2/market/ticker/one?symbol=RIF%2FBTC"
    _coinpair    = RIF_BTC
    _max_time_without_price_change = 0 # zero means infinity

    def _map(self, data):
        return {
            'price':  data['data']['latestPrice'],
            'volume': data['data']['volume24h'] }



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
