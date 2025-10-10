from engine_base import EngineWebScraping, USD_ARS_CCL
from decimal     import Decimal


to_dec = lambda x: Decimal(str(x).replace('.', '').replace(',', '.'))


class Engine(EngineWebScraping):

    _name        = EngineWebScraping._name_from_file(__file__)
    _description = "Infobae"
    _uri         = "https://www.infobae.com/economia/divisas/dolar-hoy/"
    _coinpair    = USD_ARS_CCL

    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _scraping(self, html):
        value = None
        for s in html.find_all ('div', attrs={'class':'exchange-dolar-item'}):
            d = list(map(lambda x: x.strip(), s.strings))
            if len(d)==6 and d[0]=='Contado con Liqui':
                try:
                    value = to_dec(d[2])
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
