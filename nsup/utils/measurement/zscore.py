from ._protocol import MeasurementUtilProtocol
from os import sep
from pandas import read_excel


class ZScore(MeasurementUtilProtocol):
    _required_keys = ["z_score_key", "Возраст", "Пол", "Масса тела", "Рост", "ИМТ"]
    data_path = sep.join(__file__.split(sep)[:-3]) + sep + "data/z_score/{}/{}-{}5-{}.xlsx"
    path_pts = {"Рост": ["H", "h"],
                "Масса тела": ["W", "w"],
                "ИМТ": ["BMI", "bmi"]}

    @classmethod
    def compute_reverse(cls, **kwargs):
        gender_key = "f" if kwargs["Пол"] == "Женский" else "m"
        age_key = "b" if kwargs["Возраст"]["д"] <= 1856 else "a"

        tab_path = cls.data_path.format(*cls.path_pts[kwargs["z_score_key"]],
                                        age_key,
                                        gender_key)
        tab = read_excel(tab_path)
        ref_age_key = "Day" if age_key == "b" else "Month"
        self_age_key = "д" if age_key == "b" else "м"
        self_age = kwargs["Возраст"][self_age_key]

        tgt_row = tab[tab[ref_age_key] == self_age]
        try:
            M = tgt_row.values[0][2]
        except IndexError:
            return None

        return M * (kwargs["Рост"]["м"] ** 2)

    @classmethod
    def compute(cls, **kwargs):
        cls._assert_keys(list(kwargs.keys()))

        gender_key = "f" if kwargs["Пол"] == "Женский" else "m"
        age_key = "b" if kwargs["Возраст"]["д"] <= 1856 else "a"

        tab_path = cls.data_path.format(*cls.path_pts[kwargs["z_score_key"]],
                                        age_key,
                                        gender_key)
        tab = read_excel(tab_path)
        ref_age_key = "Day" if age_key == "b" else "Month"
        self_age_key = "д" if age_key == "b" else "м"
        self_age = kwargs["Возраст"][self_age_key]

        tgt_row = tab[tab[ref_age_key] == self_age]

        try:
            L, M, S = tgt_row.values[0][1:4]
        except IndexError:
            return None

        y_val = kwargs[kwargs["z_score_key"]]
        if kwargs["z_score_key"] == "Масса тела":
            y_val = y_val["кг"]
        if kwargs["z_score_key"] == "Рост":
            y_val = y_val["см"]

        # y_val = y_val.value
        z_ind = ((y_val / M) ** L - 1) / (S * L)

        if abs(z_ind) <= 3 or kwargs["z_score_key"] == "Рост":
            return z_ind

        if z_ind > 3:
            sd3pos = M * (1 + L * S * 3) ** (1 / L)
            sd23pos = M * (1 + L * S * 3) ** (1 / L) - M * (1 + L * S * 2) ** (1 / L)
            return 3 + (y_val - sd3pos) / sd23pos

        sd3neg = M * (1 + L * S * (-3)) ** (1 / L)
        sd23neg = M * (1 + L * S * (-2)) ** (1 / L) - M * (1 + L * S * (-3)) ** (1 / L)
        return -3 + (y_val - sd3neg) / sd23neg
