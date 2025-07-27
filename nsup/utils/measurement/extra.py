from ._protocol import MeasurementUtilProtocol


class NoProteinKCal(MeasurementUtilProtocol):
    _required_keys = ["Тек*Растворы ПЭП", "ПЭП"]
    name = "Тек*Небелковые ккал"

    @classmethod
    def compute(cls, **kwargs):
        cls._assert_keys(list(kwargs.keys()))

        cur_parenterals = kwargs["Тек*Растворы ПЭП"]
        p_in, l_in, c_in = 0, 0, 0
        for (_, par) in cur_parenterals.items():
            if par is None:
                continue
            if len(par["Название раствора для ПЭП"]) == 0:
                continue

            p_in += kwargs["ПЭП"][par["Название раствора для ПЭП"]].get("Белок/100мл", 0) / 100 * par.get("Объем раствора в сутки", 0)
            l_in += kwargs["ПЭП"][par["Название раствора для ПЭП"]].get("Жиры/100мл", 0) / 100 * par.get("Объем раствора в сутки", 0)
            c_in += kwargs["ПЭП"][par["Название раствора для ПЭП"]].get("Углеводы/100мл", 0) / 100 * par.get("Объем раствора в сутки", 0)

        if p_in != 0:
            return (l_in * 9 + c_in * 4) / p_in
        else:
            return 0


class Toxicity(MeasurementUtilProtocol):
    _required_keys = ["Мочевина",
                      "Тек*Небелковые ккал",
                      "Получает препараты с почечной токсичностью",
                      "Сколько дней назад был последний прием пищи (смеси)"]
    name = "Ожидаемая токсичность"

    @classmethod
    def compute(cls, **kwargs):
        cls._assert_keys(list(kwargs.keys()))

        return max(
            0,
            int((kwargs["Мочевина"] > kwargs["Max*Мочевина"]) * (kwargs["Тек*Небелковые ккал"] < 25)),
            int(kwargs["Сколько дней назад был последний прием пищи (смеси)"] >= 3),
            kwargs["Получает препараты с почечной токсичностью"]
        )