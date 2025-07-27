from pulp import LpProblem, LpVariable, LpStatus, LpMinimize, lpSum, PULP_CBC_CMD


class EnteralSelector:
    @classmethod
    def compute(cls, patient, demands, enterals, enteral_tags, sipping, excluded_item_ids=None):
        ps = cls._p_en_f(patient["Возраст"]["лет"], demands["ККал"]["value"])
        ls = cls._l_en_f(patient["Возраст"]["лет"], demands["ККал"]["value"])
        cs = cls._c_en_f(patient["Возраст"]["лет"], demands["ККал"]["value"])

        prob = cls._make_problem(ps, ls, cs,
                                 demands["ККал"]["value"],
                                 # patient["fractions"]["сипинг" if sipping else "зонд"],
                                 1,  # patient["enteral_tags"]["no_sip" if sipping else "no_en"],
                                 enterals,
                                 enteral_tags,
                                 patient["enteral_tags"],
                                 patient["Масса тела"]["кг"] if patient["Идеальная масса тела"] is None else patient["Идеальная масса тела"]["кг"],
                                 patient["Возраст"]["лет"],
                                 sipping,
                                 disabled=excluded_item_ids)
        return cls._solve(prob, enterals)

    @classmethod
    def _make_problem(cls,
                      Ps, Ls, Cs, Es, f,
                      enterals,
                      enteral_tags,
                      tag_weights,
                      m, age_years,
                      sipping=True,
                      disabled=None):
        """
        Ps, Ls, Cs, Es - посчитанные по формулам белок, жиры, углеводы, ккал
        f - доля питания
        m - масса, кг
        """
        M = 1e7

        prob = LpProblem("en-selection", LpMinimize)

        P = LpVariable("P")
        L = LpVariable("L")
        C = LpVariable("C")
        E = LpVariable("E")

        en_weights = {k: sum([(tag in en_tags) * weight
                              for tag, weight in tag_weights.items()])
                      for k, en_tags in enteral_tags.items()}

        # i'th enteral chosen or not
        xs = LpVariable.dicts("x",
                              (i for i in range(len(enterals))),
                              cat="Binary")
        ent_doses = LpVariable.dicts("xv",
                                     (i for i in range(len(enterals))),
                                     cat="Continuous",
                                     lowBound=0)

        f1, f2 = LpVariable("abs_plc_delta"), LpVariable("n_nutritions")
        f3, f4 = LpVariable("cvk_selection"), LpVariable("total_volume")
        f5, f6 = LpVariable("tagging"), LpVariable("sipping_tube")

        if disabled is None:
            disabled = []
        for i, (name, features) in enumerate(enterals.items()):
            if "Углеводы/100мл" not in features:
                disabled += [i]

        prob += P * f == lpSum([features["Белок/100мл"] * ent_doses[i]
                                for i, (name, features) in enumerate(enterals.items()) if i not in disabled])
        prob += L * f == lpSum([features["Жиры/100мл"] * ent_doses[i]
                                for i, (name, features) in enumerate(enterals.items()) if i not in disabled])
        prob += C * f == lpSum([features["Углеводы/100мл"] * ent_doses[i]
                                for i, (name, features) in enumerate(enterals.items()) if i not in disabled])
        prob += E * f == lpSum([features["ККал/100мл"] * ent_doses[i]
                                for i, (name, features) in enumerate(enterals.items()) if i not in disabled])

        for i in range(len(enterals)):
            prob += ent_doses[i] <= xs[i] * M

        for i, (nutr_name, par) in enumerate(enterals.items()):
            if ("Возраст" not in par) or (age_years < par["Возраст"]):
                prob += xs[i] == 0
            if disabled is not None and nutr_name in disabled:
                prob += xs[i] == 0
            if sipping and "Сипинг" not in enteral_tags[nutr_name]:
                prob += xs[i] == 0

        mp, ml, mc, me = LpVariable("mp"), LpVariable("ml"), LpVariable("mc"), LpVariable("me")

        prob += mp >= P - Ps
        prob += mp >= Ps - P
        prob += ml >= L - Ls
        prob += ml >= Ls - L
        prob += mc >= C - Cs
        prob += mc >= Cs - C
        prob += me >= E - Es
        prob += me >= Es - E

        prob += lpSum([ent_doses[i] for i in range(len(enterals))]) >= 1

        prob += f1 == mp + ml + mc
        prob += f2 == me
        prob += f4 == lpSum([ent_doses[i] for i in range(len(enterals))])
        prob += f5 == -lpSum([en_weights[k] * xs[i]
                              for i, k in enumerate(list(enterals.keys()))])
        prob += f6 == -sipping * lpSum([xs[i] * ("Сипинг" in v)
                                        for i, (k, v) in enumerate(enteral_tags.items())]) - (1 - sipping) * lpSum(
            [xs[i] * ("Зонд/г-стома" in v)
             for i, (k, v) in enumerate(enteral_tags.items())])

        # MARK: no more than 3 items selected!
        prob += lpSum([xs[i] for i in range(len(enterals))]) <= 1

        c1, c2, c3, c4, c5, c6 = 1, 10, 0, 1, 10, 10
        prob += c1 * f1 + c2 * f2 + c4 * f4 + c5 * f5 + c6 * f6  # c3 * f3 +
        # prob += lpSum([xs[i] for i in range(len(enterals))])

        return prob

    @classmethod
    def _solve(cls, lp_prob, enterals):
        lp_prob.solve(PULP_CBC_CMD(msg=1))

        if LpStatus[lp_prob.status] != "Optimal":
            print(lp_prob.constraints)

            raise Exception(f"LP Status: {LpStatus[lp_prob.status]}")
            return None

        prob_vars = lp_prob.variablesDict()
        out_demands = {key: prob_vars[key].value()
                       for key in ["P", "L", "C", "E"]}
        out_enterals = {}
        for i in range(len(enterals)):
            if prob_vars[f"x_{i}"].value() == 1 and prob_vars[f"xv_{i}"].value() > 0:
                val = prob_vars[f'xv_{i}'].value() * 100
                val = round(val / 10) * 10
                out_enterals[list(enterals.keys())[i]] = val

        return out_demands, out_enterals

    @classmethod
    def _p_en_f(cls, age: int, energy: float) -> float:
        """
        Количество белков от общей калорийности по данным рекомендаций для энтерального питания

        :param age: возраст пациента в месяцах
        :param energy: возраст пациента в месяцах
        :return: количество углеводов в граммах для энтерального питания
        """

        age_to_coefs = {
            1: 0.074,
            2: 0.09,
            3: 0.103,
            4: 0.12
        }
        i = (age >= 0) + (age >= 4) + (age >= 7) + (age >= 13)
        coef_p = age_to_coefs[i]

        return coef_p * energy / 4

    @classmethod
    def _l_en_f(cls, age: int, energy: float) -> float:
        """
        Количество жиров от общей калорийности по данным рекомендаций для энтерального питания

        :param age: возраст пациента в месяцах
        :param energy: возраст пациента в месяцах
        :return: количество жиров в граммах для энтерального питания
        """

        age_to_coefs = {
            1: 0.49,
            2: 0.464,
            3: 0.437,
            4: 0.3
        }
        i = (age >= 0) + (age >= 4) + (age >= 7) + (age >= 13)
        coef_l = age_to_coefs[i]

        return coef_l * energy / 9

    @classmethod
    def _c_en_f(cls, age: int, energy: float) -> float:
        """
        Количество углеводов от общей калорийности по данным рекомендаций для энтерального питания

        :param age: возраст пациента в месяцах
        :param energy: возраст пациента в месяцах
        :return: количество углеводов в граммах для энтерального питания
        """

        age_to_coefs = {
            1: 0.436,
            2: 0.446,
            3: 0.459,
            4: 0.58
        }
        i = (age >= 0) + (age >= 4) + (age >= 7) + (age >= 13)
        coef_c = age_to_coefs[i]

        return coef_c * energy / 4
