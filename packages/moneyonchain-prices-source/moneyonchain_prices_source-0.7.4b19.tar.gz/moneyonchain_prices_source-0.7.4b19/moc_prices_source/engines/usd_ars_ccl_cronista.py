from engine_base import EngineWebScraping, USD_ARS_CCL
from decimal     import Decimal


to_dec = lambda x: Decimal(str(x).replace('.', '').replace(',', '.'))


class Engine(EngineWebScraping):

    _name        = EngineWebScraping._name_from_file(__file__)
    _description = "Cronista.com"
    _uri         = "https://www.cronista.com/MercadosOnline/moneda.html?id=ARSCONT"
    _coinpair    = USD_ARS_CCL

    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity


    def _scraping(self, html):
        value = None
        for s in html.find_all ('table', id="market-scrll-1"):
            d = list(map(lambda x: x.strip(), s.strings))
            if len(d)==10 and d[0]=='DÓLAR CCL GD30 48HS' and d[1]=='Compra' and d[2]=='$' and d[4]=='Venta' and d[5]=='$':
                try:
                    value = (to_dec(d[3]) + to_dec(d[6]))/Decimal(2) 
                except:
                    value = None
                if value:
                    break
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
    
