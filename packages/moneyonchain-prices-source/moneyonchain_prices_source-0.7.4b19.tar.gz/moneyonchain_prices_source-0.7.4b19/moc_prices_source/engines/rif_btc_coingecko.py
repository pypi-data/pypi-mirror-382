from engine_base import Base, RIF_BTC


class Engine(Base):

    _name = Base._name_from_file(__file__)
    _description = "Coingecko"
    _uri = "https://api.coingecko.com/api/v3/simple/price?ids=rif-token&vs_currencies=btc&include_24hr_vol=true"
    _coinpair = RIF_BTC
    _max_time_without_price_change = 0  # zero means infinity

    def _map(self, data):
        return {"price": data["rif-token"]['btc'], "volume": data["rif-token"]['btc_24h_vol']}


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)