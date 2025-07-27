from ._step_protocol import NutritionDerivationProtocol


class CarbohydrateDerivation(NutritionDerivationProtocol):
    @classmethod
    def compute(cls, patient, **kwargs):
        c_min = cls._c_min(patient["Активность пациента"] == "активен и мобилен",
                           patient["Активность пациента"] == "активность ограничена",
                           patient["Активность пациента"] == "тяжелое состояние - требует поддержки жизненных функций",
                           patient["Масса тела"]["кг"])
        c_max = cls._c_max(patient["Активность пациента"] == "активен и мобилен",
                           patient["Активность пациента"] == "активность ограничена",
                           patient["Активность пациента"] == "тяжелое состояние - требует поддержки жизненных функций",
                           patient["Масса тела"]["кг"],
                           patient["Cколько часов в сутках доступно для потенциального ПЭП"])

        carbohydrates_due = cls._carbohydrates_due(c_min, c_max,
                                                   patient[
                                                       "Тяжелая белково-энергетическая недостаточность"],
                                                   patient[
                                                       "Умеренная белково-энергетическая недостаточность"],
                                                   patient[
                                                       "Легкая белково-энергетическая недостаточность"],
                                                   patient["Нормальный нутритивный статус"],
                                                   patient["Избыточная масса тела"],
                                                   patient["Ожирение 1 степени"] + patient[
                                                       "Ожирение 2 степени"] + patient[
                                                       "Ожирение 3 степени"] + patient[
                                                       "Ожирение тяжелое"])

        if "due_only" in kwargs:
            return carbohydrates_due

        carbohydrates = cls._carbohydrates(c_min, c_max,
                                           patient["Глюкоза"],
                                           patient["Лактат"],
                                           patient["Тяжелая белково-энергетическая недостаточность"],
                                           patient["Умеренная белково-энергетическая недостаточность"],
                                           patient["Легкая белково-энергетическая недостаточность"],
                                           patient["Нормальный нутритивный статус"],
                                           patient["Избыточная масса тела"],
                                           patient["Ожирение 1 степени"] + patient["Ожирение 2 степени"] + patient["Ожирение 3 степени"] + patient["Ожирение тяжелое"],
                                           patient["Риск рефидинг-синдрома"],  # TODO
                                           patient["Потребность в дотации кислорода"],
                                           patient["Частичная нутритивная поддержка"],
                                           patient["Полное восполнение питания"])
        carbohydrates_max = cls._carbohydrates_max(c_min, c_max,
                                                   patient["Глюкоза"],
                                                   patient["Лактат"],
                                                   patient["Тяжелая белково-энергетическая недостаточность"],
                                                   patient["Умеренная белково-энергетическая недостаточность"],
                                                   patient["Легкая белково-энергетическая недостаточность"],
                                                   patient["Нормальный нутритивный статус"],
                                                   patient["Избыточная масса тела"],
                                                   patient["Ожирение 1 степени"] + patient["Ожирение 2 степени"] + patient["Ожирение 3 степени"] + patient["Ожирение тяжелое"],
                                                   patient["Риск рефидинг-синдрома"],  # TODO
                                                   patient["Потребность в дотации кислорода"],
                                                   patient["Частичная нутритивная поддержка"],
                                                   patient["Полное восполнение питания"])

        return carbohydrates, [c_min, carbohydrates_max], carbohydrates_due

    @classmethod
    def _c_min(cls, m: int, s: int, v: int, weight: float) -> float:
        """
        Нижняя граница количества углеводов на кг массы тела по данным рекомендаций

        :param m: пациент активен и мобилен (параметр - активность)
        :param s: пациент с ограниченной активностью, но стабильный (параметр - активность)
        :param v: пациент нуждается в поддержке жизненных функций (параметр - активность)
        :param weight: масса тела пациента
        :return: нижняя граница рекомендуемого количества углеводов (в граммах) на кг массы тела
        """

        weight_to_coefs = {
            1: (2.9, 5.8, 8.6),
            2: (2.2, 2.8, 4.3),
            3: (1.4, 2.2, 4.3),
            4: (0.7, 1.4, 2.9)
        }
        i = (weight >= 0.0) + (weight >= 11.0) + (weight >= 31.0) + (weight >= 45)
        coef_v, coef_s, coef_m = weight_to_coefs[i]

        return coef_m * m + coef_s * s + coef_v * v

        # weight_to_coefs = {
        #     1: (2.9, 5.8, 8.6),
        #     2: (2.2, 2.8, 4.3),
        #     3: (1.4, 2.2, 4.3),
        #     4: (0.7, 1.4, 2.9)
        # }
        # i = (weight >= 0.0) + (weight >= 11.0) + (weight >= 31.0) + (weight >= 45)
        # coef_m, coef_s, coef_v = weight_to_coefs[i]
        #
        # return coef_m * m + coef_s * s + coef_v * v

    @classmethod
    def _c_max(cls, m: int, s: int, v: int, weight: float, pep_hours) -> float:
        """
        Верхняя граница количества углеводов на кг массы тела по данным рекомендаций

        :param m: пациент активен и мобилен (параметр - активность)
        :param s: пациент с ограниченной активностью (параметр - активность)
        :param v: пациент нуждается в поддержке жизненных функций (параметр - активность)
        :param weight: масса тела пациента
        :return: верхняя граница рекомендуемого количества углеводов (в граммах) на кг массы тела
        """

        weight_to_coefs = {
            1: (5.8, 8.6, 14),
            2: (3.6, 5.8, 8.6),
            3: (2.2, 4.3, 5.8),
            4: (1.4, 2.9, 4.3)
        }
        i = (weight >= 0.0) + (weight >= 11.0) + (weight >= 31.0) + (weight >= 45)
        coef_v, coef_s, coef_m = weight_to_coefs[i]

        return coef_m * m + coef_s * s + coef_v * v

        # weight_to_coefs = {
        #     1: (5.8, 8.6, 14),
        #     2: (3.6, 5.8, 8.6),
        #     3: (2.2, 4.3, 5.8),
        #     4: (1.4, 2.9, 4.3)
        # }
        # i = (weight >= 0.0) + (weight >= 11.0) + (weight >= 31.0) + (weight >= 45)
        # coef_m, coef_s, coef_v = weight_to_coefs[i]
        #
        # return min(coef_m * m + coef_s * s + coef_v * v,
        #            0.5 * weight * pep_hours)

    @classmethod
    def _carbohydrates(
            cls,
            c_min: float,
            c_max: float,
            glc: float,
            lac: float,
            sev_maln: int,
            mod_maln: int,
            mild_maln: int,
            norm_ns: int,
            overweight: int,
            obesity: int,
            refeeding: float,
            oxyg: int,
            part_ns: int,
            full_ns: int) -> float:
        """
        Количество углеводов на кг массы тела данного пациента

        :param c_max: максимальное количество углеводов на кг массы тела для пациента
        :param c_min: минимальное количество углеводов на кг массы тела для пациента
        :param glc: концентрация глюкозы, ммоль/л
        :param lac: концентрация лактата, ммоль/л
        :param sev_maln: наличие тяжелой БЭН
        :param mod_maln: наличие умеренной БЭН
        :param mild_maln: наличие легкой БЭН
        :param norm_ns: наличие нормального нутритивного статуса
        :param overweight: наличие избытка массы тела
        :param obesity: наличие ожирения
        :param refeeding: риск рефидинг-синдрома
        :param oxyg: потребность в кислороде
        :param part_ns: нужна ли пациенту частичная нутритивная поддержка
        :param full_ns: нужна ли пациенту полное восполнение питания
        :return: количество углеводов на кг массы тела
        """
        k = (c_max - c_min) / 6
        c = (c_min + (
                (6 * k * sev_maln + 5 * k * mod_maln + 4 * k * mild_maln + 3 * k * norm_ns + 3 * k * overweight + 3 * k * obesity) / (
                        1 + refeeding + int(glc > 8) * 0.25 + int(lac > 2.2) * 0.25 + oxyg * 0.25))) * (0.5 * part_ns + full_ns)

        return min(c, c_max)

    @classmethod
    def _carbohydrates_max(
            cls,
            c_min: float,
            c_max: float,
            glc: float,
            lac: float,
            sev_maln: int,
            mod_maln: int,
            mild_maln: int,
            norm_ns: int,
            overweight: int,
            obesity: int,
            refeeding: float,
            oxyg: int,
            part_ns: int,
            full_ns: int) -> float:
        """
        Максимальное количество углеводов для данного пациента - количество углеводов
        на кг массы тела для пациента с меньшим z-score ИМТ, но теми же ограничивающими факторами

        :param c_max: максимальное количество углеводов на кг массы тела для пациента
        :param c_min: минимальное количество углеводов на кг массы тела для пациента
        :param glc: концентрация глюкозы, ммоль/л
        :param lac: концентрация лактата, ммоль/л
        :param sev_maln: наличие тяжелой БЭН
        :param mod_maln: наличие умеренной БЭН
        :param mild_maln: наличие легкой БЭН
        :param norm_ns: наличие нормального нутритивного статуса
        :param overweight: наличие избытка массы тела
        :param obesity: наличие ожирения
        :param refeeding: риск рефидинг-синдрома
        :param oxyg: потребность в кислороде
        :param part_ns: нужна ли пациенту частичная нутритивная поддержка
        :param full_ns: нужна ли пациенту полное восполнение питания
        :return: максимальное количество углеводов на кг массы тела
        """

        # меняем значения нутритивного статуса - перемещаемся в соседний (по мере уменьшения z-score)
        # интервал ИМТ - из легкой БЭН в умеренную, из ожирения - в избыточную массу тела и т.д.
        nutr_status = list(map(int, [sev_maln, mod_maln, mild_maln, norm_ns, overweight, obesity]))
        one_ind = nutr_status.index(1)
        prev_one_ind = max(one_ind - 1, 0)
        nutr_status[one_ind], nutr_status[prev_one_ind] = nutr_status[prev_one_ind], nutr_status[one_ind]
        sev_maln, mod_maln, mild_maln, norm_ns, overweight, obesity = nutr_status

        # расчет гипотетической потребности в нутриенте после сдвига нутритивного статуса
        k = (c_max - c_min) / 6
        c = (c_min + (
                (
                            6 * k * sev_maln + 5 * k * mod_maln + 4 * k * mild_maln + 3 * k * norm_ns + 3 * k * overweight + 3 * k * obesity) / (
                        1 + refeeding + int(glc > 8) * 0.25 + int(lac > 2.2) * 0.25 + oxyg * 0.25))) * (
                    0.5 * part_ns + full_ns)

        return min(c, c_max)

    @classmethod
    def _carbohydrates_due(
            cls,
            c_min: float,
            c_max: float,
            sev_maln: int,
            mod_maln: int,
            mild_maln: int,
            norm_ns: int,
            overweight: int,
            obesity: int) -> float:
        """
        Должное количество углеводов на кг массы тела для таких пациентов - т.е. без
        учета персональных ограничивающих факторов


        :param c_max: максимальное количество углеводов на кг массы тела для пациента
        :param c_min: минимальное количество углеводов на кг массы тела для пациента
        :param sev_maln: наличие тяжелой БЭН
        :param mod_maln: наличие умеренной БЭН
        :param mild_maln: наличие легкой БЭН
        :param norm_ns: наличие нормального нутритивного статуса
        :param overweight: наличие избытка массы тела
        :param obesity: наличие ожирения
        :param refeeding: риск рефидинг-синдрома
        :return: должное количество углеводов на кг массы тела
        """

        glc = 4.0
        lac = 1.5
        refeeding = 0
        oxyg = 0
        part_ns = 0
        full_ns = 1

        k = (c_max - c_min) / 6
        c = (c_min + (
                (
                            6 * k * sev_maln + 5 * k * mod_maln + 4 * k * mild_maln + 3 * k * norm_ns + 3 * k * overweight + 3 * k * obesity) / (
                        1 + refeeding + int(glc > 8.0) * 0.25 + int(lac > 2.2) * 0.25 + oxyg * 0.25))) * (
                    0.5 * part_ns + full_ns)

        return min(c, c_max)
