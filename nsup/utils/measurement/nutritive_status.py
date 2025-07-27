from ._protocol import MeasurementUtilProtocol


class NormalNutritiveStatus(MeasurementUtilProtocol):
    _required_keys = ["Возраст", "z-score ИМТ", "z-score массы тела"]
    name = "Нормальный нутритивный статус"

    @classmethod
    def compute(cls, **kwargs):
        return -1 <= (kwargs["z-score массы тела"] if kwargs["Возраст"]["лет"] < 6 else kwargs["z-score ИМТ"]) <= 1


class LightProteinCalorieDeficiency(MeasurementUtilProtocol):
    _required_keys = ["Возраст", "z-score ИМТ", "z-score массы тела"]
    name = "Легкая белково-энергетическая недостаточность"

    @classmethod
    def compute(cls, **kwargs):
        return -2 <= (kwargs["z-score массы тела"] if kwargs["Возраст"]["лет"] < 6 else kwargs["z-score ИМТ"]) < -1


class MediumProteinCalorieDeficiency(MeasurementUtilProtocol):
    _required_keys = ["Возраст", "z-score ИМТ", "z-score массы тела"]
    name = "Умеренная белково-энергетическая недостаточность"

    @classmethod
    def compute(cls, **kwargs):
        return -3 <= (kwargs["z-score массы тела"] if kwargs["Возраст"]["лет"] < 6 else kwargs["z-score ИМТ"]) < -2


class AcuteProteinCalorieDeficiency(MeasurementUtilProtocol):
    _required_keys = ["Возраст", "z-score ИМТ", "z-score массы тела"]
    name = "Тяжелая белково-энергетическая недостаточность"

    @classmethod
    def compute(cls, **kwargs):
        return -10 <= (kwargs["z-score массы тела"] if kwargs["Возраст"]["лет"] < 6 else kwargs["z-score ИМТ"]) < -3


class Overweight(MeasurementUtilProtocol):
    _required_keys = ["z-score ИМТ"]
    name = "Избыточная масса тела"

    @classmethod
    def compute(cls, **kwargs):
        return 1 < kwargs["z-score ИМТ"] < 2


class Obesity1(MeasurementUtilProtocol):
    _required_keys = ["z-score ИМТ"]
    name = "Ожирение 1 степени"

    @classmethod
    def compute(cls, **kwargs):
        return 2 <= kwargs["z-score ИМТ"] < 2.5


class Obesity2(MeasurementUtilProtocol):
    _required_keys = ["z-score ИМТ"]
    name = "Ожирение 2 степени"

    @classmethod
    def compute(cls, **kwargs):
        return 2.5 <= kwargs["z-score ИМТ"] < 3


class Obesity3(MeasurementUtilProtocol):
    _required_keys = ["z-score ИМТ"]
    name = "Ожирение 3 степени"

    @classmethod
    def compute(cls, **kwargs):
        return 3 <= kwargs["z-score ИМТ"] < 4


class ObesitySevere(MeasurementUtilProtocol):
    _required_keys = ["z-score ИМТ"]
    name = "Ожирение тяжелое"

    @classmethod
    def compute(cls, **kwargs):
        return 3 <= kwargs["z-score ИМТ"]   # < 10
