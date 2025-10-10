from engine_base import Base, USD_MXN
from decimal     import Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Bitso.com"
    _uri         = "https://api.bitso.com/v3/ticker/?book=usd_mxn"
    _coinpair    = USD_MXN

    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _map(self, data):
        try:
            volume = Decimal(data['payload']['volume'])
        except:
            volume = None        
        try:
            value = Decimal(data['payload']['last'])
        except:
            value = None
        out = {'price':  value}
        if volume:
            out['volume'] = volume
        return out


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
