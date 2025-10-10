from engine_base import Base, BTC_ARS
from decimal import Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Ripio"
    _uri         = "https://app.ripio.com/api/v3/public/rates"
    _coinpair    = BTC_ARS
    
    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _map(self, data):
        value = {}
        for i in data:
            if i['ticker']=='BTC_ARS':
                value['price'] = (Decimal(i['buy_rate']) + Decimal(i['sell_rate'])) / Decimal('2')
                break
        return value


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
