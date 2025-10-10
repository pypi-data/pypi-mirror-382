from engine_base import Base, DOC_USD
from decimal import Decimal
import datetime

class Engine(Base):
    _name = Base._name_from_file(__file__)
    _description = "Dummy"
    _coinpair = DOC_USD
    _uri = None

    def __call__(self, start_time=None):
        if start_time is None:
            start_time = datetime.datetime.now()
        self._clean_output_values()
        self._price = Decimal('1')
        self._volume = Decimal('0')
        self._timestamp = self._now()
        self._last_change_timestamp = self._timestamp
        self._time = datetime.datetime.now() - start_time
        self._age = None
        self._error = None
        return True


if __name__ == '__main__':
    print("File: {}, Ok!".format(repr(__file__)))
    engine = Engine()
    engine()
    if engine.error:
        print(f"{engine} Error: {engine.error}")
    else:
        print(engine)
