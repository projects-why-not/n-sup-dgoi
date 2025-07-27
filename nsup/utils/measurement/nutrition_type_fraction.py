from ._protocol import MeasurementUtilProtocol


class NutritionTypeFractions(MeasurementUtilProtocol):
    @classmethod
    def compute(cls, demands, **kwargs):
        # FIXME! ML or from form!
        # return cls.get_from_nutritionist(demands, **kwargs)
        return cls.get_from_form(**kwargs)

    @classmethod
    def get_from_form(cls, **kwargs):
        return {"сипинг": kwargs["Доля энтерального питания (сипинг)"] / 100,
                "зонд": kwargs["Доля энтерального питания (зонд/стома)"] / 100,
                "ПЭП": kwargs["Доля парентерального питания"] / 100}

    @classmethod
    def get_from_nutritionist(cls, demands, **kwargs):
        sip, ent = [0] * 2
        parent = {"Белок/100мл": 0,
                  "Жиры/100мл": 0,
                  "Углеводы/100мл": 0}

        for _, v in kwargs["Смеси ЭП"].items():
            name = v["Название смеси для ЭП"]
            if len(name) == 0:
                continue
            is_sip = v["Способ получения"] == "сипинг"
            volume = v["Объем смеси в сутки"]

            if is_sip:
                sip += kwargs["ЭП"][name]["ККал/100мл"] / 100 * volume
            else:
                ent += kwargs["ЭП"][name]["ККал/100мл"] / 100 * volume

        for _, v in kwargs["Растворы ПЭП"].items():
            name = v["Название раствора для ПЭП"]
            if len(name) == 0:
                continue
            volume = v["Объем раствора в сутки"]
            for k in parent.keys():
                parent[k] += kwargs["ПЭП"][name][k] / 100 * volume / kwargs["Масса тела"]["кг"]

        return {"сипинг": sip / demands["ККал"]["due"],
                "зонд": ent / demands["ККал"]["due"],
                "ПЭП": sum([v / demands[k.split("/")[0]]["due"]
                            for k, v in parent.items()]) / 3}
