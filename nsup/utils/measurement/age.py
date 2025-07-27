from ._protocol import MeasurementUtilProtocol
from ..age import Age


class Ager(MeasurementUtilProtocol):
    _required_keys = ["Дата консультации", "Дата рождения"]
    name = "Возраст"

    @classmethod
    def compute(cls, **kwargs):
        cls._assert_keys(list(kwargs.keys()))

        return Age(kwargs["Дата консультации"],
                   kwargs["Дата рождения"])
