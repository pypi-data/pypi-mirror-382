from engine_base import Base, BTC_ARS
from decimal import Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "belo.app"
    _uri         = "https://api.belo.app/public/price"
    _coinpair    = BTC_ARS
    
    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _map(self, data):
        value = {}
        for i in data:
            if i['pairCode']=='BTC/ARS':
                value['price'] = (Decimal(i['ask']) + Decimal(i['bid'])) / Decimal('2')
                break
        return value


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
