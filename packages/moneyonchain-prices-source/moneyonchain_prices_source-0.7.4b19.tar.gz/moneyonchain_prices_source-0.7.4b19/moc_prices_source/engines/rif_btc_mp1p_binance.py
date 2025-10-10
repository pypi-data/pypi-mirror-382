from engine_base import BaseWithFailover, RIF_BTC_MP1P
from rif_btc_binance import Engine as RifBtcEngine
from decimal import Decimal

base_uri = "https://{}/api/v3/depth?symbol=RIFBTC"
factor = 0.01

class Engine(BaseWithFailover):

    _name         = BaseWithFailover._name_from_file(__file__)
    _description  = "Binance"
    _uri          = base_uri.format("api.binance.com")
    _uri_failover = base_uri.format("moc-proxy-api-binance.moneyonchain.com")
    _coinpair     = RIF_BTC_MP1P
    _max_time_without_price_change = 0 # zero means infinity



    def __call__(self):
        price_engine = RifBtcEngine()
        ok = price_engine()
        self._error = price_engine.error
        self.base_price = price_engine.price
        if ok:
            ok = BaseWithFailover.__call__(self)
        return ok
    


    def _map(self, data):

        value = Decimal(0)

        if 'bids' in data.keys() and 'asks' in data.keys():
            lv = []
            for t in ['asks', 'bids']:
                data[t].sort(reverse=(t=='bids'))
                v = Decimal('0')
                for p, q in data[t]:
                    p, q = Decimal(str(p)), Decimal(str(q))
                    d = abs((self.base_price / p) - Decimal('1'))
                    if d>=Decimal(str(factor)):
                        q = Decimal('1')
                    v += (q*p)
                    if d>=Decimal(str(factor)):
                        break
                lv.append(v)
            value = min(lv)



        return {
            'price':  value}


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(f"URI = {repr(engine.uri)}")
    print()
    print(engine)
    print()
    if engine.error:
        print()
        print(engine.error)
        print()
