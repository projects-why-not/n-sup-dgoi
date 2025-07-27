from ._protocol import MeasurementUtilProtocol
from ..age import Age
import warnings


class ALF(MeasurementUtilProtocol):
    _required_keys = ["Билирубин общий", "АЛТ", "АСТ", "Max*АСТ", "Min*АЛТ"]
    name = "Острая печеночная недостаточность"

    @classmethod
    def compute(cls, **kwargs):
        cls._assert_keys(list(kwargs.keys()))

        # 1
        if kwargs["Билирубин общий"] <= kwargs["Max*Билирубин общий"]:
            return False
        # 2
        if kwargs["АЛТ"] > kwargs["Max*АЛТ"]:
            pass
        else:
            return False
        '''
        if kwargs["Возраст"] < Age(1,0) and kwargs["АЛТ"] > 56:
            pass
        elif Age(1,0) <= kwargs["Возраст"] <= Age(6,11) and kwargs["АЛТ"] > 29:
            pass
        elif kwargs["Возраст"] >= Age(7,0) and kwargs["АЛТ"] > 37:
            pass
        else:
            return False
        '''

        # 3
        if kwargs["АСТ"] > kwargs["Max*АСТ"]:
            pass
        else:
            return False
        '''
        if kwargs["Возраст"] < Age(1,0) and kwargs["АСТ"] > 58:
            pass
        elif Age(1,0) <= kwargs["Возраст"] <= Age(3,11) and kwargs["АЛТ"] > 59:
            pass
        elif Age(4,0) <= kwargs["Возраст"] <= Age(6,11) and kwargs["АЛТ"] > 48:
            pass
        elif Age(7,0) <= kwargs["Возраст"] <= Age(12,11) and kwargs["АЛТ"] > 44:
            pass
        elif Age(13,0) <= kwargs["Возраст"] and kwargs["АЛТ"] > 39:
            pass
        else:
            return False
        '''

        return True


class AKI(MeasurementUtilProtocol):
    _required_keys = ["СКФ", "Цистатин C", "Мочевина", "Тек*Небелковые ккал"]
    name = "Острое повреждение почек"

    @classmethod
    def compute(cls, **kwargs):
        cls._assert_keys(list(kwargs.keys()))

        return max(0,
                   (kwargs["Цистатин C"] > kwargs["Max*Цистатин C"]),
                   (kwargs["СКФ"] < 60),
                   int((kwargs["Мочевина"] > kwargs["Max*Мочевина"]) * (kwargs["Тек*Небелковые ккал"] >= 25))
                   )


class GFR(MeasurementUtilProtocol):
    _required_keys = ["Возраст", "Пол", "Креатинин"]
    name = "СКФ"

    @classmethod
    def compute(cls, **kwargs):
        cls._assert_keys(list(kwargs.keys()))

        if kwargs["Пол"] == "Женский":
            k = 0.368
        else:
            if kwargs["Возраст"] <= Age(12,0):
                k = 0.368
            else:
                k = 0.413

        return (k * kwargs["Рост"]["см"]) / (kwargs["Креатинин"] / 88.4)


class VisceralPoolProteinDeficiency(MeasurementUtilProtocol):
    _required_keys = ["Альбумин", "Min*Альбумин"]
    name = "Дефицит висцерального пула белка"

    @classmethod
    def compute(cls, **kwargs):
        cls._assert_keys(list(kwargs.keys()))
        return kwargs["Альбумин"] < kwargs["Min*Альбумин"]


class Cholestasis(MeasurementUtilProtocol):
    _required_keys = ["Билирубин прямой",
                      "Щелочная фосфатаза",
                      "Гамма-глутамилтрансфераза",
                      "Max*Щелочная фосфатаза",
                      "Max*Гамма-глутамилтрансфераза"]
    name = "Лабораторные признаки холестаза"

    @classmethod
    def compute(cls, **kwargs):
        cls._assert_keys(list(kwargs.keys()))

        alp_rel = kwargs["Щелочная фосфатаза"] / kwargs["Max*Щелочная фосфатаза"]
        dir_bil = kwargs["Билирубин прямой"]
        ggt_rel = kwargs["Гамма-глутамилтрансфераза"] / kwargs["Max*Гамма-глутамилтрансфераза"]

        ch = ((alp_rel >= 1.5) and (ggt_rel >= 3.0)) + 0.5 * (dir_bil > kwargs["Max*Билирубин прямой"] and (
                (alp_rel >= 1.5) or (ggt_rel >= 3.0)))
        return min(1, ch)


class AcutePancreatite(MeasurementUtilProtocol):
    _required_keys = ["Липаза", "Амилаза", "Max*Амилаза", "Max*Липаза"]
    name = "Лабораторные признаки острого панкреатита"

    @classmethod
    def compute(cls, **kwargs):
        cls._assert_keys(list(kwargs.keys()))

        lipase_rel = kwargs["Липаза"] / kwargs["Max*Липаза"]
        amylase_rel = kwargs["Амилаза"] / kwargs["Max*Амилаза"]

        return int((lipase_rel >= 3) + (amylase_rel >= 3) >= 1)


class RefeedingRisk(MeasurementUtilProtocol):
    _required_keys = ["Сколько дней назад был последний прием пищи (смеси)",
                      "Тяжелая белково-энергетическая недостаточность",
                      "Умеренная белково-энергетическая недостаточность",
                      "Легкая белково-энергетическая недостаточность",
                      "Вес снижается (не набирается для <1 года)",
                      # TODO: fill parameters
                      ]
    name = "Риск рефидинг-синдрома"

    @classmethod
    def compute(cls, **kwargs):
        # warnings.warn("0 in refeeding!")
        # return 0

        cur_nutr = {k: 0 for k in ["Белок", "Жиры", "Углеводы", "ККал"]}
        type_keys = {"Смеси ЭП": "смеси",
                     "Растворы ПЭП": "раствора"}
        for _type in ["Смеси ЭП", "Растворы ПЭП"]:
            for _, nutr_item in kwargs.get("Тек*" + _type, {}).items():
                name = nutr_item[f"Название {type_keys[_type]} для {_type.split()[-1]}"]
                if name is None or len(name) == 0:
                    continue

                amount = nutr_item[f"Объем {type_keys[_type]} в сутки"]
                print(amount)
                for nutr_key in cur_nutr:
                    cur_nutr[nutr_key] = cur_nutr[nutr_key] + kwargs[_type.split()[-1]][name].get(f"{nutr_key}/100мл", 0) * amount / 100

        for key in ["Белок", "Жиры", "Углеводы"]:
            cur_nutr[key] = cur_nutr[key] / kwargs["Масса тела"]["кг"]

        cur_nutr_fractions = {k: cur_nutr[k] / kwargs[k + "_due"]
                              for k in cur_nutr}
        cur_par_frac = sum([cur_nutr_fractions[nutr_key]
                            for nutr_key in list(cur_nutr.keys())[:-1]]) / 3
        cur_ent_frac = cur_nutr_fractions["ККал"]

        return cls.refeeding_f(kwargs["Сколько дней назад был последний прием пищи (смеси)"],
                               kwargs["Тяжелая белково-энергетическая недостаточность"],
                               kwargs["Умеренная белково-энергетическая недостаточность"],
                               kwargs["Легкая белково-энергетическая недостаточность"],
                               kwargs["Калий"] / kwargs["Min*Калий"],
                               kwargs["Фосфор неорганический"] / kwargs["Min*Фосфор неорганический"],
                               kwargs["Магний общий"] / kwargs["Min*Магний общий"],
                               kwargs["Вес снижается (не набирается для <1 года)"],
                               cur_ent_frac,
                               cur_par_frac,
                               kwargs["Каким питание было ранее (до консультации)"] == "сниженное питание",
                               kwargs["Как давно такое питание"] == "менее 3 дней",
                               kwargs["Как давно такое питание"] == "3-4 дня",
                               kwargs["Как давно такое питание"] == "5-6 дней",
                               kwargs["Как давно такое питание"] == "7 или более дней")

    @classmethod
    def refeeding_f(cls,
                    last_meal: int,
                    sev_maln: int,
                    mod_maln: int,
                    mild_maln: int,
                    k_rel: float,
                    p_rel: float,
                    mg_rel: float,
                    weight_loss: int,
                    EN_now_part: float,
                    PEN_now_part: float,
                    meals_few: int,
                    meals_long_1: int,
                    meals_long_2: int,
                    meals_long_3: int,
                    meals_long_4: int
                    ) -> float:
        """
        Вероятность развития синдрома возобновления питания

        :param last_meal: последний прием пищи, в днях
        :param sev_maln: наличие тяжелой БЭН
        :param mod_maln: наличие умеренной БЭН
        :param mild_maln: наличие легкой БЭН
        :param k_rel: калий относительно нижнего порога нормы, в долях
        :param p_rel: форфор неорганический относительно нижнего порога нормы, в долях
        :param mg_rel: магний общий относительно нижнего порога нормы, в долях
        :param weight_loss: потеря веса / отсутствие прибавки в раннем возрасте - t/f
        :param EN_now_part: доля получемого сейчас ЭП относительно потребности
        :param PEN_now_part: доля получемого сейчас ПЭП относительно потребности
        :param meals_few: питание до консультации (нормальное, сниженное, повышенное) == сниженное
        :param meals_long_1: такое питание у пациента на протяжении 0-2 дней
        :param meals_long_2: такое питание у пациента на протяжении 3-4 дней
        :param meals_long_3: такое питание у пациента на протяжении 5-6 дней
        :param meals_long_4: такое питание у пациента на протяжении 7 дней и более
        :return: вероятность развития синдрома возобновления питания, 0.0-1.0
        """

        K_P_Mg = ((k_rel < 0.75) or (p_rel < 0.75) or (mg_rel < 0.75)) * 0.33 + (
                (k_rel < 0.5) or (p_rel < 0.5) or (mg_rel < 0.5)) * 0.17

        refeed = (0.33 * mild_maln) + (0.5 * mod_maln) + (1.0 * sev_maln) + (
                0.33 * weight_loss) + K_P_Mg + ((
                                                        0.33 * (last_meal >= 3) + 0.17 * (last_meal >= 5) + 0.5 * (
                                                            last_meal >= 7)) + (
                                                        meals_few * ((meals_long_1 * 0) + (meals_long_2 * 0.34) + (
                                                            meals_long_3 * 0.17) + (meals_long_4 * 0.5)))) * (
                         (EN_now_part + PEN_now_part) <= 0.75)

        return min(1, refeed)
