
from ._protocol import MeasurementUtilProtocol


class EnteralTagging(MeasurementUtilProtocol):
    name = "enteral_tags"
    weights = {'polymeric': 1, 'olygomeric': 1,
               'hepa': 2, 'renal': 2, 'pulmo': 2, 'diab': 2, 'stand': 2,
               'isocal': 3, 'hypocal': 3, 'hypercal': 3,
               'probio': 4, 'no_probio': 4,
               'fiber': 5, 'no_fiber': 5,
               'lactose': 6, 'no_lactose': 6,
               'no_sip': 0, "no_en": 0
               }
    trans = {"polymeric": "Полимерная",
             "olygomeric": "Олигомерная",
             "hepa": "Гепа",
             "renal": "Нефро",
             "pulmo": "Пульмо",
             "diab": "Диабет",
             "stand": "Стандартная",
             "isocal": "Изокалорическая",
             "hypocal": "Гипокалорическая",
             "hypercal": "Гиперкалорическая",
             "probio": "Содержит пробиотики",
             "no_probio": "Без пробиотиков",
             "fiber": "Содержит пищевые волокна",
             "no_fiber": "Без пищевых волокон",
             "lactose": "Содержит лактозу",
             "no_lactose": "Без лактозы",
             "no_sip": "no_sip",
             "no_en": "no_en"
             }

    @classmethod
    def compute(cls, **kwargs):
        tag_vals = {
            "malabs_st": cls.malabs_st_f(kwargs["Возраст"]["лет"],
                                         kwargs["Характер стула"],
                                         kwargs["Кратность стула"]),
            "no_en": cls.no_en_f(kwargs["Желудочно-кишечное кровотечение"],
                                 kwargs["Кишечная непроходимость"],
                                 kwargs["Другие противопоказания к энтеральному питанию"]),
            "no_probio": cls.no_probio_f(kwargs["Лейкоциты"]["Лейкоциты"],
                                         kwargs["Этап терапии"],
                                         kwargs["День от начала этапа терапии"]),
            "no_fiber": cls.no_fiber_f(kwargs["Характер стула"]),
            "no_lactose": cls.no_lactose_f(kwargs["Характер стула"]),

            "hepa": cls.hepa_f(kwargs["Острая печеночная недостаточность"],
                               kwargs["Хроническая печеночная недостаточность"],
                               kwargs["Лабораторные признаки холестаза"]),
            "renal": cls.renal_f(kwargs["Острое повреждение почек"],
                                 kwargs["Хроническая болезнь почек"]),
            "pulmo": cls.pulmo_f(kwargs["Потребность в дотации кислорода"]),
        }

        cur_parenterals = kwargs["Тек*Растворы ПЭП"]
        c_in = 0
        for (_, par) in cur_parenterals.items():
            if par is None:
                continue
            if len(par["Название раствора для ПЭП"]) == 0:
                continue
            c_in += kwargs["ПЭП"][par["Название раствора для ПЭП"]].get("Углеводы/100мл", 0) / 100 * par.get("Объем раствора в сутки", 0)

        tag_vals.update({"no_sip": cls.no_sip_f(kwargs["Неврологические проблемы, препятствующие пероральной алиментации"],
                                                kwargs["Другие противопоказания (стриктуры, свищи, послеоперационные раны и проч) к пероральной алиментации"],
                                            tag_vals["no_en"]),
                         "olygomeric": cls.olygomeric_f(kwargs["Аллергия к белкам коровьего молока"],
                                                        tag_vals["malabs_st"],
                                                        kwargs["Мальабсорбция по данным копрограммы"]),
                         "probio": cls.probio_f(tag_vals["no_probio"]),
                         "fiber": cls.fiber_f(tag_vals["no_fiber"]),
                         "lactose": cls.lactose_f(tag_vals["no_lactose"]),
                         "diab": cls.diab_f(kwargs["Сахарный диабет"],
                                            kwargs["Глюкоза"]["Глюкоза"],
                                            int(c_in > 0)),
                         })
        tag_vals.update({"stand": cls.stand_f(tag_vals["hepa"], tag_vals["renal"], tag_vals["pulmo"], tag_vals["diab"]),
                         "hypocal": cls.hypocal_f(kwargs["Кровь в стуле"], kwargs["Характер стула"],
                                                  kwargs["Лабораторные признаки острого панкреатита"]),
                         "hypercal": cls.hypercal_f(kwargs["Мальабсорбция по данным копрограммы"],
                                                    tag_vals["malabs_st"],
                                                    kwargs["Лабораторные признаки острого панкреатита"],
                                                    kwargs["Риск рефидинг-синдрома"],
                                                    kwargs["Лабораторные признаки холестаза"]),

                         })
        tag_vals.update({"isocal": cls.isocal_f(tag_vals["hypercal"], tag_vals["hypocal"]),
                         "polymeric": cls.polymeric_f(tag_vals["olygomeric"])})

        return {cls.trans[k]: cls.tag_hierarchy_f(k, tag_vals[k])
                for k in cls.weights}

    @classmethod
    def no_en_f(cls, gib: int, bowel_obstr: int, no_en_int: int) -> int:
        """
        Запрет на проведение энтерального питания.

        :param gib: "желудочно-кишечное кровотечение"
        :param bowel_obstr: "кишечная непроходимость"
        :param no_en_int: "другие препятствия для ЭП"
        :return: запрет на проведение энтерального питания: T/F
        """

        return min(1, gib + bowel_obstr + no_en_int)

    @classmethod
    def no_sip_f(cls, bulb: int, no_per_os: int, no_en: int) -> int:
        """
        Запрет на прием смеси через рот.

        :param bulb: "бульбарные нарушения"
        :param no_per_os: "другие препятствия для приема смеси per os"
        :param no_en: результат функции no_en_f (запрет на ЭП)
        :return: запрет на прием смеси через рот: T/F
        """

        return min(1, bulb + no_per_os + no_en)

    @classmethod
    def malabs_st_f(cls, age: int, feces: str, freq_feces: str) -> int:
        """
        Мальабсорбция по характеру стула.

        :param age: возраст в годах, полных лет
        :param feces: "характер стула"
        :param freq_feces: "частота стула"
        :return: мальабсорбция по характеру стула: T/F
        """
        a = (feces == "водянистый") + (
                (freq_feces == "3 или больше") * (age >= 1) * (feces == "плотная кашица")) + (
                    ((freq_feces == "1-2") + (freq_feces == "3 или больше")) * (age >= 1) * (feces == "жидкая кашица"))

        return min(1, a)

    @classmethod
    def olygomeric_f(cls, ACMP: int, malabs_st: int, malabsorption: int) -> float:
        """
        Вероятность для тега "олигомерная".

        :param ACMP: АБКМ
        :param malabs_st: результат функции malabs_st_f
        :param malabsorption: "мальабсорбция по данным копрограммы"
        :return: вероятность применимости смеси с тегом "олигомерная"
        """
        return min(1, 0.1 + (ACMP * 0.9) + (malabs_st * 0.8) + (malabsorption * 0.8))

    @classmethod
    def polymeric_f(cls, olygomeric: float) -> float:
        """
        Вероятность для тега "полимерная".

        :param olygomeric: результат функции olygomeric_f
        :return: вероятность применимости смеси с тегом "полимерная"
        """
        return 1 - olygomeric

    @classmethod
    def no_probio_f(cls, leu: float, ther_stage: str, ther_stage_day: int) -> float:
        """
        Вероятность для тега "без пробиотиков".

        :param leu: число лейкоцитов "Лейкоциты"
        :param ther_stage: "этап терапии"
        :param ther_stage_day: "день от начала этапа"
        :return: вероятность применимости смеси с тегом "без пробиотиков"
        """
        return min(1, 0.5 + ((leu <= 1.5) * 0.5 + (
                (ther_stage == "ТГСК") * (ther_stage_day < 100) * 0.5) + (
                                     (ther_stage == "период после блока ПХТ") * (ther_stage_day < 14) * 0.5)))

    @classmethod
    def probio_f(cls, no_probio: float) -> float:
        """
        Вероятность для тега "Пробиотики".

        :param no_probio: результат функции no_probio_f
        :return: вероятность применимости смеси с тегом "Пробиотики"
        """
        return 1 - no_probio

    @classmethod
    def no_fiber_f(cls, feces: str) -> float:
        """
        Вероятность для тега "без пищевых волокон".

        :param feces: "характер стула"
        :return: вероятность применимости смеси с тегом "без пищевых волокон"
        """
        return min(1, 0.5 - 0.4 * (feces == "фрагментированный") + (
                feces == "водянистый") * 0.5 + (
                           feces == "жидкая кашица") * 0.45 + (
                           feces == "плотная кашица") * 0.4)

    @classmethod
    def fiber_f(cls, no_fiber: float) -> float:
        """
        Вероятность для тега "Пищевые волокна".

        :param no_fiber: результат функции no_fiber_f
        :return: вероятность применимости смеси с тегом "Пищевые волокна"
        """
        return 1 - no_fiber

    @classmethod
    def no_lactose_f(cls, feces: str) -> float:
        """
        Вероятность для тега "без лактозы".

        :param feces: "характер стула"
        :return: вероятность применимости смеси с тегом "без лактозы"
        """
        return min(1, 0.5 + (
                feces == "водянистый") * 0.5 + (
                           feces == "жидкая кашица") * 0.45 + (
                           feces == "плотная кашица") * 0.4)

    @classmethod
    def lactose_f(cls, no_lactose: float) -> float:
        """
        Вероятность для тега "Лактоза".

        :param no_lactose: результат функции no_lactose_f
        :return: вероятность применимости смеси с тегом "Лактоза"
        """
        return 1 - no_lactose

    @classmethod
    def hepa_f(cls, ahi: int, chd: int, cholestasis: float) -> float:
        """
        Вероятность для тега "Гепа".

        :param ahi: наличие острой печеночной недостаточности по б/х
        :param chd: "Хроническая печеночная недостаточность"
        :param cholestasis: результат функции cholestasis_f
        :return: вероятность применимости смеси с тегом "Гепа"
        """
        return min(1, 0.1 + 0.8 * ahi + 0.8 * chd + 0.8 * cholestasis)

    @classmethod
    def renal_f(cls, aki: int, ckd: int) -> float:
        """
        Вероятность для тега "Нефро".

        :param aki: наличие острой почечной недостаточности по б/х
        :param ckd: "Хроническая болезнь почек"
        :return: вероятность применимости смеси с тегом "Нефро"
        """
        return min(1, 0.1 + 0.8 * aki + 0.8 * ckd)

    @classmethod
    def pulmo_f(cls, oxy: int) -> float:
        """
        Вероятность для тега "Пульмо".

        :param oxy: "Потребность в дотации кислорода"
        :return: вероятность применимости смеси с тегом "Пульмо"
        """
        return min(1, 0.1 + 0.8 * oxy)

    @classmethod
    def diab_f(cls, diab: int, glu: float, glu_PN: int) -> float:
        """
        Вероятность для тега "Диабет".

        :param diab: "Сахарный диабет"
        :param glu: концентрация глюкозы в крови
        :param glu_PN: получает ли глюкозу в составе ПЭП
        :return: вероятность применимости смеси с тегом "Диабет"
        """
        return min(1, 0.1 + 0.8 * diab + 0.5 * (glu >= 8.0) * (glu_PN == 0))

    @classmethod
    def stand_f(cls, hepa: float, renal: float, pulmo: float, diab: float) -> float:
        """
        Вероятность для тега "Стандартная".

        :param hepa: результат функции hepa_f
        :param renal: результат функции renal_f
        :param pulmo: результат функции pulmo_f
        :param diab: результат функции diab_f
        :return: вероятность применимости смеси с тегом "Стандартная"
        """
        return max(0.1, 1 - max(hepa, renal, pulmo, diab))

    @classmethod
    def hypocal_f(cls, blood_st: int, feces: str, pancr: int) -> float:
        """
        Вероятность для тега "Гипокалорическая".

        :param blood_st: "Кровь в стуле"
        :param feces: "характер стула"
        :param pancr: результат функции pancr_f
        :return: вероятность применимости смеси с тегом "Гипокалорическая"
        """
        return 0.1 + blood_st * 0.1 + (feces == "водянистый") * 0.2 + pancr * 0.1

    @classmethod
    def hypercal_f(cls, malabsorption: int, malabs_st: int, pancr: int, refeeding: float, cholestasis: float) -> float:
        """
        Вероятность для тега "Гиперкалорическая".

        :param malabsorption: "мальабсорбция по данным копрограммы"
        :param malabs_st: результат функции malabs_st_f
        :param pancr: результат функции pancr_f
        :param refeeding: результат функции refeeding_f
        :param cholestasis: результат функции cholestasis_f
        :return: вероятность применимости смеси с тегом "Гиперкалорическая"
        """
        return max(0, 0.4 - refeeding * 0.3 - malabsorption * 0.4 - malabs_st * 0.4 - pancr * 0.4 - cholestasis * 0.4)

    @classmethod
    def isocal_f(cls, hypercal: float, hypocal: float) -> float:
        """
        Вероятность для тега "Изокалорическая".

        :param hypercal: результат функции hypercal_f
        :param hypocal: результат функции hypocal_f
        :return: вероятность применимости смеси с тегом "Изокалорическая"
        """
        return max(0.1, 1 - hypercal - hypocal)

    @classmethod
    def tag_hierarchy_f(cls, tag: str, tag_value: float) -> float:
        """
        Вероятность для любого тега с учетом его места в иерархии.

        :param tag: непосредственно название тега
        :param tag_value: результат функции *tag-name*_f либо значение из таблицы смесей (для рассчета расстояний)
        :return: вероятность тега с учетом иерархии
        """

        ## названия тегов в словаре заменить на те, которые фигурируют в базе данных смесей и растворов

        a = 1

        return tag_value * (a / (2 ** cls.weights[tag]))
