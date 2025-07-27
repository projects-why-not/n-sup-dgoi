from ._protocol import MeasurementUtilProtocol


class BMI(MeasurementUtilProtocol):
    _required_keys = ["Масса тела", "Рост"]
    name = "ИМТ"

    @classmethod
    def compute(cls, **kwargs):
        cls._assert_keys(list(kwargs.keys()))
        w = kwargs["Масса тела"]["кг"]
        h = kwargs["Рост"]["м"]
        bmi = w / (h * h)

        return bmi
