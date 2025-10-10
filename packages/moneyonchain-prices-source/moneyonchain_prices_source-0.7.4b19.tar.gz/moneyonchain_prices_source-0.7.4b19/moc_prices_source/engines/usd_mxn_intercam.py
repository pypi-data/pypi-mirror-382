from engine_base import Base, USD_MXN
from decimal     import Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "Intercam.com.mx"
    _method      = "post"
    _uri         = "https://intercamprod.finsol.cloud/services/historico/getLast"
    _payload     = '{"type":"ticker","chain":true,"rics":["MXN=X"],"comentarios":"","user":"intercam.widgets@financialsolutions.mx"}'
    _coinpair    = USD_MXN

    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _map(self, data):
        values = [
            data['data']["MXN=X"]['last']['cfbid'],
            data['data']["MXN=X"]['last']['cfask']
        ]
        values = list(map(lambda x: Decimal(str(x).replace(',', '.')), values))
        value = sum(values)/len(values)
        return {
            'price':  value
        }


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
