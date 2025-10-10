from engine_base import EngineWebScraping, USD_ARS
from decimal     import Decimal


to_dec = lambda x: Decimal(str(x).replace('.', '').replace(',', '.'))


class Engine(EngineWebScraping):

    _name        = EngineWebScraping._name_from_file(__file__)
    _description = "InfoDolar.com"
    _uri         = "https://www.infodolar.com/cotizacion-dolar-blue.aspx"
    _coinpair    = USD_ARS

    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity


    def _scraping(self, html):
        value = None
        table = html.find('table', id="CompraVenta")
        if table:
            values = []
            for s in table.find_all ('td', attrs={'class':'colCompraVenta'} ):
                d = to_dec(list(map(lambda x: x.strip(), s.strings))[0
                    ].replace('$', '').strip())
                values.append(d)
            if len(values)==2:
                try:
                    value = (Decimal(values[0]) + Decimal(values[1]))/Decimal(2) 
                except:
                    value = None

        if not value:
            self._error = "Response format error"
            return None
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
    
