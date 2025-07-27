from ._protocol import MeasurementUtilProtocol
from .zscore import ZScore
from ..value import Value


class PerfectMass(MeasurementUtilProtocol):
    @classmethod
    def compute(cls, **kwargs):
        if kwargs["Ожирение 1 степени"] + kwargs["Ожирение 2 степени"] + kwargs["Ожирение 3 степени"] + kwargs["Ожирение тяжелое"] == 0:
            return None

        m = ZScore.compute_reverse(z_score_key="ИМТ",
                                   **kwargs)
        return Value(m, "кг")
