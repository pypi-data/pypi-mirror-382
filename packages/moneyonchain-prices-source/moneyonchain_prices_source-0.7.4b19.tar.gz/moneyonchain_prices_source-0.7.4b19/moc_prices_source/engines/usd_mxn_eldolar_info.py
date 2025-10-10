from engine_base import EngineWebScraping, USD_MXN
from decimal     import Decimal


class Engine(EngineWebScraping):

    _name        = EngineWebScraping._name_from_file(__file__)
    _description = "ElDolar.info"
    _uri         = "https://www.eldolar.info/es-MX/mexico/dia/hoy"
    _coinpair    = USD_MXN

    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity

    def _scraping(self, html):
        value = None
        for s in html.find_all ('span', attrs={'class':'xTimes'}):
            d = list(map(lambda x: x.strip(), s.parent.strings))
            if len(d)==4 and d[0]=="1" and d[1]=="Dólar =" and d[3]=="Pesos":
                try:
                    value = Decimal(d[2])
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
