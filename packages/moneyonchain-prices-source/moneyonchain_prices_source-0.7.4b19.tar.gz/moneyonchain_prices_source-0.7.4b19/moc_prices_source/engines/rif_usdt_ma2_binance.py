from engine_base import RIF_USDT_MA2, get_env
from decimal import Decimal
from rif_usdt_ma_binance import Engine as Base

max_quantity = Decimal(get_env('MA_MAX2_QUANTITY', '200000'))

class Engine(Base):

    _name         = Base._name_from_file(__file__)
    _coinpair     = RIF_USDT_MA2
    _max_quantity = max_quantity

if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(f"URI = {repr(engine.uri)}")
    print(f"MAX_QUANTITY = {max_quantity}")
    print()
    print(engine)
    print()
    if engine.error:
        print()
        print(engine.error)
        print()
