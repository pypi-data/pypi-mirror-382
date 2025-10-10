from engine_base import Base, BTC_ARS
from decimal import Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "ArgenBTC"
    _uri         = "https://argenbtc.com/cotizacion"
    _coinpair    = BTC_ARS
    
    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _map(self, data):
        value = {}
        value['price'] = (Decimal(data['precio_compra']) + Decimal(data['precio_venta'])) / Decimal('2')
        return value


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
