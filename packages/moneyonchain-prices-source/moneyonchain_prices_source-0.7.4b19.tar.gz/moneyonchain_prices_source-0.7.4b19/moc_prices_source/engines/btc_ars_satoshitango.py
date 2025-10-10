from engine_base import Base, BTC_ARS


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "satoshitango.com"
    _uri         = "https://api.satoshitango.com/v3/ticker/ARS/BTC"
    _coinpair    = BTC_ARS
    
    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _map(self, data):
        return {
            'price': data['data']['ticker']['BTC']['bid'],
            'volume': data['data']['ticker']['BTC']['volume']
        }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
