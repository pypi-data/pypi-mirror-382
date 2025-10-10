from engine_base import Base, USD_COP


class Engine(Base):

    _name        = Base._name_from_file(__file__)
    _description = "BanRep"
    _uri         = "https://totoro.banrep.gov.co/estadisticas-economicas/rest/consultaDatosService/consultaMercadoCambiario"
    _coinpair    = USD_COP

    def _map(self, data):
        return {'price': data[-1][1]}


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    print(engine)
    if engine.error:
        print(engine.error)
