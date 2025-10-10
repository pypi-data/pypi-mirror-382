from engine_base import Base, USD_MXN
from decimal     import Decimal


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "CitiBanamex"
    _uri         = "https://finanzasenlinea.infosel.com/banamex/WSFeedJSON/service.asmx/DivisasLast?callback="
    _coinpair    = USD_MXN

    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _map(self, data):
        value = None
        for i in data:
            if i['cveInstrumento']=="MXNUS":
                values = [
                    i['ValorActualCompra'],
                    i['ValorActualVenta']
                ]
                values = list(map(lambda x: Decimal(str(x).replace(',', '.')), values))
                value = sum(values)/len(values)
                break
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
