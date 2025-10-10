from engine_base import EngineWebScraping, USD_COP
from decimal import Decimal, InvalidOperation


to_dec = lambda x: Decimal(
    str(x).replace('$', '')
          .replace(',', '')
          .strip())


class Engine(EngineWebScraping):

    _name        = EngineWebScraping._name_from_file(__file__)
    _description = "DolarHoy.co"
    _uri         = "https://www.dolarhoy.co"
    _coinpair    = USD_COP

    _max_age                       = 3600 # 1hs.
    _max_time_without_price_change = 0    # zero means infinity


    def _scraping(self, html):
        
        value = None
        values = []
        
        for t in html.find_all ('h3'):
            if t.string:
                if set(t.string.lower().split()).issuperset(
                        {'precio', 'casas', 'cambio'}):
                    for s in t.parent.strings:
                        try:
                            v = to_dec(s)
                        except InvalidOperation:
                            v = None
                        if v is not None:
                            values.append(v)
        
        if len(values)==2:
            value = sum(values)/2

        if not value:
            self._error = "Response format error"
            return None

        return {
            'price': value
        }



if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
    
