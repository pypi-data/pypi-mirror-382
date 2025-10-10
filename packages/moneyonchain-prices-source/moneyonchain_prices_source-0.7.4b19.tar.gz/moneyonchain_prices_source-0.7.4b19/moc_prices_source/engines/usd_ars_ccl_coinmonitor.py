from engine_base import Base, USD_ARS_CCL


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "CoinMonitor.info"
    _uri         = "https://coinmonitor.info/chart_DOLARES_24hs.json"
    _coinpair    = USD_ARS_CCL
    
    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _map(self, data):
        return {
            'price':  data[0][3]
        }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
