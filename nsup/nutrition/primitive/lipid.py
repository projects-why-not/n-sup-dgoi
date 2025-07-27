from ._step_protocol import NutritionDerivationProtocol


class LipidDerivation(NutritionDerivationProtocol):
    @classmethod
    def compute(cls, patient, **kwargs):
        l_min = cls._l_min()
        l_max = cls._l_max(patient["Масса тела"]["кг"],
                           patient["Cколько часов в сутках доступно для потенциального ПЭП"])

        lipids_due = cls._lipids_due(l_max,
                                     patient["Тяжелая белково-энергетическая недостаточность"],
                                     patient["Умеренная белково-энергетическая недостаточность"],
                                     patient["Легкая белково-энергетическая недостаточность"],
                                     patient["Нормальный нутритивный статус"],
                                     patient["Избыточная масса тела"],
                                     patient["Ожирение 1 степени"] + patient["Ожирение 2 степени"] +
                                     patient["Ожирение 3 степени"] + patient["Ожирение тяжелое"])

        if "due_only" in kwargs:
            return lipids_due

        lipids = cls._lipids(l_max,
                             patient["Триглицериды"],
                             patient["Этап терапии"] == "CAR T-Cells терапия",
                             patient["Лабораторные признаки холестаза"],
                             patient["Лабораторные признаки острого панкреатита"],
                             patient["Тяжелая белково-энергетическая недостаточность"],
                             patient["Умеренная белково-энергетическая недостаточность"],
                             patient["Легкая белково-энергетическая недостаточность"],
                             patient["Нормальный нутритивный статус"],
                             patient["Избыточная масса тела"],
                             patient["Ожирение 1 степени"] + patient["Ожирение 2 степени"] + patient["Ожирение 3 степени"] + patient["Ожирение тяжелое"],
                             patient["Риск рефидинг-синдрома"],  # TODO
                             patient["Острая печеночная недостаточность"],
                             patient["Частичная нутритивная поддержка"],
                             patient["Полное восполнение питания"])
        lipids_max = cls._lipids_max(l_max,
                                     patient["Триглицериды"],
                                     patient["Этап терапии"] == "CAR T-Cells терапия",
                                     patient["Лабораторные признаки холестаза"],
                                     patient["Лабораторные признаки острого панкреатита"],
                                     patient["Тяжелая белково-энергетическая недостаточность"],
                                     patient["Умеренная белково-энергетическая недостаточность"],
                                     patient["Легкая белково-энергетическая недостаточность"],
                                     patient["Нормальный нутритивный статус"],
                                     patient["Избыточная масса тела"],
                                     patient["Ожирение 1 степени"] + patient["Ожирение 2 степени"] + patient["Ожирение 3 степени"] + patient["Ожирение тяжелое"],
                                     patient["Риск рефидинг-синдрома"],
                                     patient["Острая печеночная недостаточность"],
                                     patient["Частичная нутритивная поддержка"],
                                     patient["Полное восполнение питания"])

        return lipids, [l_min, lipids_max], lipids_due

    @classmethod
    def _l_min(cls) -> float:
        """
        Минимальное количество жиров на кг массы тела

        :return: количество жиров на кг массы тела
        """
        return 0.0

    @classmethod
    def _l_max(cls, w_kg, pep_hours) -> float:
        """
        Максимальное количество жиров на кг массы тела

        :return: количество жиров на кг массы тела
        """
        return min(3.0,
                   0.13 * w_kg * pep_hours)

    @classmethod
    def _lipids(
            cls,
            l_max: float,
            tg: float,
            car_t: int,
            cholestasis: int,
            pancr: int,
            sev_maln: int,
            mod_maln: int,
            mild_maln: int,
            norm_ns: int,
            overweight: int,
            obesity: int,
            refeeding: float,
            alf: int,
            part_ns: int,
            full_ns: int) -> float:
        """
        Количество жиров на кг массы тела данного пациента

        :param l_max: максимальное количество жиров на кг массы тела для пациента
        :param tg: концентрация триглицердов в крови, ммоль/л
        :param car_t: пациент на этапе CAR T-cells терапии
        :param cholestasis: лабораторные признаки холестаза
        :param pancr: лабораторные признаки панкреатита
        :param sev_maln: наличие тяжелой БЭН
        :param mod_maln: наличие умеренной БЭН
        :param mild_maln: наличие легкой БЭН
        :param norm_ns: наличие нормального нутритивного статуса
        :param overweight: наличие избытка массы тела
        :param obesity: наличие ожирения
        :param refeeding: риск рефидинг-синдрома
        :param alf: лабораторные признаки острой печеночной недостаточности
        :param part_ns: нужна ли пациенту частичная нутритивная поддержка
        :param full_ns: нужна ли пациенту полное восполнение питания
        :return: количество жиров на кг массы тела
        """
        k = l_max / 6
        l = (1 - (int(tg >= 4))) * (1 - car_t) * (
                (
                            6 * k * sev_maln + 5 * k * mod_maln + 4 * k * mild_maln + 3 * k * norm_ns + 3 * k * overweight + 3 * k * obesity) / (
                        1 + (int(tg > 3)) + pancr + refeeding + alf + cholestasis)) * (
                    0.5 * part_ns + full_ns)
        l_min = 0

        return max(l_min, l)

    @classmethod
    def _lipids_max(
            cls,
            l_max: float,
            tg: float,
            car_t: int,
            cholestasis: int,
            pancr: int,
            sev_maln: int,
            mod_maln: int,
            mild_maln: int,
            norm_ns: int,
            overweight: int,
            obesity: int,
            refeeding: float,
            alf: int,
            part_ns: int,
            full_ns: int) -> float:
        """
        Максимальное количество жиров для данного пациента - количество жиров
        на кг массы тела для пациента с меньшим z-score ИМТ, но теми же ограничивающими факторами

        :param l_max: максимальное количество жиров на кг массы тела для пациента
        :param tg: концентрация триглицердов в крови, ммоль/л
        :param car_t: пациент на этапе CAR T-cells терапии
        :param cholestasis: лабораторные признаки холестаза
        :param pancr: лабораторные признаки панкреатита
        :param sev_maln: наличие тяжелой БЭН
        :param mod_maln: наличие умеренной БЭН
        :param mild_maln: наличие легкой БЭН
        :param norm_ns: наличие нормального нутритивного статуса
        :param overweight: наличие избытка массы тела
        :param obesity: наличие ожирения
        :param refeeding: риск рефидинг-синдрома
        :param alf: лабораторные признаки острой печеночной недостаточности
        :param part_ns: нужна ли пациенту частичная нутритивная поддержка
        :param full_ns: нужна ли пациенту полное восполнение питания
        :return: максимальное количество жиров на кг массы тела
        """

        # меняем значения нутритивного статуса - перемещаемся в соседний (по мере уменьшения z-score)
        # интервал ИМТ - из легкой БЭН в умеренную, из ожирения - в избыточную массу тела и т.д.
        nutr_status = list(map(int, [sev_maln, mod_maln, mild_maln, norm_ns, overweight, obesity]))
        one_ind = nutr_status.index(1)
        prev_one_ind = max(one_ind - 1, 0)
        nutr_status[one_ind], nutr_status[prev_one_ind] = nutr_status[prev_one_ind], nutr_status[one_ind]
        sev_maln, mod_maln, mild_maln, norm_ns, overweight, obesity = nutr_status

        # расчет гипотетической потребности в нутриенте после сдвига нутритивного статуса
        k = l_max / 6
        l = (1 - (int(tg >= 4))) * (1 - car_t) * (
                (
                            6 * k * sev_maln + 5 * k * mod_maln + 4 * k * mild_maln + 3 * k * norm_ns + 3 * k * overweight + 3 * k * obesity) / (
                        1 + (int(tg > 3)) + pancr + refeeding + alf + cholestasis)) * (
                    0.5 * part_ns + full_ns)
        l_min = 0

        return max(l_min, l)

    @classmethod
    def _lipids_due(
            cls,
            l_max: float,
            sev_maln: int,
            mod_maln: int,
            mild_maln: int,
            norm_ns: int,
            overweight: int,
            obesity: int) -> float:
        """
        Должное количество жиров на кг массы тела для таких пациентов - т.е. без
        учета персональных ограничивающих факторов

        :param l_max: максимальное количество жиров на кг массы тела для пациента
        :param sev_maln: наличие тяжелой БЭН
        :param mod_maln: наличие умеренной БЭН
        :param mild_maln: наличие легкой БЭН
        :param norm_ns: наличие нормального нутритивного статуса
        :param overweight: наличие избытка массы тела
        :param obesity: наличие ожирения
        :return: количество жиров на кг массы тела
        """

        tg = 2.0
        car_t = 0
        cholestasis = 0
        pancr = 0
        refeeding = 0
        alf = 0
        part_ns = 0
        full_ns = 1

        k = l_max / 6
        l = (1 - (int(tg >= 4))) * (1 - car_t) * (
                (
                            6 * k * sev_maln + 5 * k * mod_maln + 4 * k * mild_maln + 3 * k * norm_ns + 3 * k * overweight + 3 * k * obesity) / (
                        1 + (int(tg > 3)) + pancr + refeeding + alf + cholestasis)) * (
                    0.5 * part_ns + full_ns)
        l_min = 0

        return max(l_min, l)
