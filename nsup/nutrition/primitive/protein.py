from ._step_protocol import NutritionDerivationProtocol


class ProteinDerivation(NutritionDerivationProtocol):
    @classmethod
    def compute(cls, patient, **kwargs):
        p_min = cls._p_min(patient["Возраст"]["м"])
        p_max = cls._p_max(patient["Возраст"]["м"],
                           patient["Масса тела"]["кг"],
                           patient["Cколько часов в сутках доступно для потенциального ПЭП"])

        protein_due = cls._protein_due(p_min, p_max,
                                       patient["Тяжелая белково-энергетическая недостаточность"],
                                       patient["Умеренная белково-энергетическая недостаточность"],
                                       patient["Легкая белково-энергетическая недостаточность"],
                                       patient["Нормальный нутритивный статус"],
                                       patient["Избыточная масса тела"],
                                       patient["Ожирение 1 степени"] + patient["Ожирение 2 степени"] +
                                       patient["Ожирение 3 степени"] + patient["Ожирение тяжелое"])

        if "due_only" in kwargs:
            return protein_due

        protein = cls._protein(p_min, p_max,
                               patient["Хроническая болезнь почек"], patient["Острое повреждение почек"],
                               patient["Тяжелая белково-энергетическая недостаточность"],
                               patient["Умеренная белково-энергетическая недостаточность"],
                               patient["Легкая белково-энергетическая недостаточность"],
                               patient["Нормальный нутритивный статус"],
                               patient["Избыточная масса тела"],
                               patient["Ожирение 1 степени"] + patient["Ожирение 2 степени"] + patient["Ожирение 3 степени"] + patient["Ожирение тяжелое"],
                               patient["Ожидаемая токсичность"],
                               patient["Частичная нутритивная поддержка"],
                               patient["Полное восполнение питания"],
                               patient["Риск рефидинг-синдрома"])
        protein_min = cls._protein_min(p_min, patient["Риск рефидинг-синдрома"])
        protein_max = cls._protein_max(p_min, p_max,
                                       patient["Хроническая болезнь почек"], patient["Острое повреждение почек"],
                                       patient["Тяжелая белково-энергетическая недостаточность"],
                                       patient["Умеренная белково-энергетическая недостаточность"],
                                       patient["Легкая белково-энергетическая недостаточность"],
                                       patient["Нормальный нутритивный статус"],
                                       patient["Избыточная масса тела"],
                                       patient["Ожирение 1 степени"] + patient["Ожирение 2 степени"] + patient["Ожирение 3 степени"] + patient["Ожирение тяжелое"],
                                       patient["Ожидаемая токсичность"],
                                       patient["Частичная нутритивная поддержка"],
                                       patient["Полное восполнение питания"],
                                       patient["Риск рефидинг-синдрома"])

        return protein, [protein_min, protein_max], protein_due

    @classmethod
    def _p_min(cls, age: int) -> float:
        """
        Расчет минимального количества белка на кг массы тела для пациентов данного возраста

        :param age: возраст в месяцах
        :return: количество белка на кг массы тела
        """
        return 1.5 - 0.5 * (age > 12)

    @classmethod
    def _p_max(cls, age: int, w_kg, pep_hours) -> float:
        """
        Расчет максимального количества белка на кг массы тела для пациентов данного возраста

        :param age: возраст в месяцах
        :return: количество белка на кг массы тела
        """

        return min(2.0 + 0.64 * (age <= 35),
                   0.11 * w_kg * pep_hours)

    @classmethod
    def _protein(
            cls,
            p_min_a: float,
            p_max_a: float,
            ckd: int,
            aki: int,
            sev_maln: int,
            mod_maln: int,
            mild_maln: int,
            norm_ns: int,
            overweight: int,
            obesity: int,
            tox: int,
            part_ns: int,
            full_ns: int,
            refeeding: float) -> float:
        """
        Количество белка на кг массы тела данного пациента

        :param p_min_a: минимальное количество белка на кг массы тела для пациента
        :param p_max_a: максимальное количество белка на кг массы тела для пациента
        :param ckd: наличие ХБП
        :param aki: наличие ОПП
        :param sev_maln: наличие тяжелой БЭН
        :param mod_maln: наличие умеренной БЭН
        :param mild_maln: наличие легкой БЭН
        :param norm_ns: наличие нормального нутритивного статуса
        :param overweight: наличие избытка массы тела
        :param obesity: наличие ожирения
        :param tox: есть ли риск токсичности при большом количестве нутриентов
        :param part_ns: нужна ли пациенту частичная нутритивная поддержка
        :param full_ns: нужна ли пациенту полное восполнение питания
        :param refeeding: Риск рефидинг-синдрома
        :return: количество белка на кг массы тела
        """
        k = (p_max_a - p_min_a) / 6
        p = (p_min_a + ((6 * k * sev_maln + 5 * k * mod_maln + 4 * k * mild_maln + 3 * k * norm_ns + 3 * k * overweight + 3 * k * obesity) / (
                                    1 + tox)) * (
                     1 - ckd) * (1 - aki) + aki * 0.2 * p_min_a * (1 - ckd)) / (1 + refeeding) * (0.5 * part_ns + full_ns)

        return min(p, p_max_a)

    @classmethod
    def _protein_min(cls, p_min_a, refeeding):
        return p_min_a / (1 + refeeding)

    @classmethod
    def _protein_max(
            cls,
            p_min_a: float,
            p_max_a: float,
            ckd: int,
            aki: int,
            sev_maln: int,
            mod_maln: int,
            mild_maln: int,
            norm_ns: int,
            overweight: int,
            obesity: int,
            tox: int,
            part_ns: int,
            full_ns: int,
            refeeding: float) -> float:
        """
        Максимальное количество белка для данного пациента - количество белка
        на кг массы тела для пациента с меньшим z-score ИМТ, но теми же ограничивающими факторами

        :param p_min_a: минимальное количество белка на кг массы тела для пациента
        :param p_max_a: максимальное количество белка на кг массы тела для пациента
        :param ckd: наличие ХБП
        :param aki: наличие ОПП
        :param sev_maln: наличие тяжелой БЭН
        :param mod_maln: наличие умеренной БЭН
        :param mild_maln: наличие легкой БЭН
        :param norm_ns: наличие нормального нутритивного статуса
        :param overweight: наличие избытка массы тела
        :param obesity: наличие ожирения
        :param tox: есть ли риск токсичности при большом количестве нутриентов
        :param part_ns: нужна ли пациенту частичная нутритивная поддержка
        :param full_ns: нужна ли пациенту полное восполнение питания
        :param refeeding: Риск рефидинг-сидрома
        :return: максимальное количество белка на кг массы тела
        """

        # меняем значения нутритивного статуса - перемещаемся в соседний (по мере уменьшения z-score)
        # интервал ИМТ - из легкой БЭН в умеренную, из ожирения - в избыточную массу тела и т.д.
        nutr_status = list(map(int, [sev_maln, mod_maln, mild_maln, norm_ns, overweight, obesity]))
        one_ind = nutr_status.index(1)
        prev_one_ind = max(one_ind - 1, 0)
        nutr_status[one_ind], nutr_status[prev_one_ind] = nutr_status[prev_one_ind], nutr_status[one_ind]
        sev_maln, mod_maln, mild_maln, norm_ns, overweight, obesity = nutr_status

        # расчет гипотетической потребности в нутриенте после сдвига нутритивного статуса
        k = (p_max_a - p_min_a) / 6
        p = (p_min_a + ((6 * k * sev_maln + 5 * k * mod_maln + 4 * k * mild_maln + 3 * k * norm_ns + 3 * k * overweight + 3 * k * obesity) / (
                                    1 + tox)) * (
                     1 - ckd) * (1 - aki) + aki * 0.2 * p_min_a * (1 - ckd)) / (1 + refeeding) * (0.5 * part_ns + full_ns)

        return min(p, p_max_a)

    @classmethod
    def _protein_due(
            cls,
            p_min: float,
            p_max: float,
            sev_maln: int,
            mod_maln: int,
            mild_maln: int,
            norm_ns: int,
            overweight: int,
            obesity: int) -> float:
        """
        Должное количество белка на кг массы тела для таких пациентов - т.е. без
        учета персональных ограничивающих факторов

        :param p_min: минимальное количество белка на кг массы тела для пациента
        :param p_max: максимальное количество белка на кг массы тела для пациента
        :param sev_maln: наличие тяжелой БЭН
        :param mod_maln: наличие умеренной БЭН
        :param mild_maln: наличие легкой БЭН
        :param norm_ns: наличие нормального нутритивного статуса
        :param overweight: наличие избытка массы тела
        :param obesity: наличие ожирения
        :return: должное количество белка на кг массы тела
        """
        k = (p_max - p_min) / 6
        tox = 0
        ckd = 0
        aki = 0
        full_ns = 1
        part_ns = 0
        refeeding = 0
        p = (p_min + ((6 * k * sev_maln + 5 * k * mod_maln + 4 * k * mild_maln + 3 * k * norm_ns + 3 * k * overweight + 3 * k * obesity) / (
                                  1 + tox)) * (
                     1 - ckd) * (1 - aki) + aki * 0.2 * p_min * (1 - ckd)) / (1 + refeeding) * (0.5 * part_ns + full_ns)

        return min(p, p_max)

