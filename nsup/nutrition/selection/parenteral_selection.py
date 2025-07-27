# from pulp import LpProblem, LpVariable, LpStatus, LpMinimize, lpSum
#
#
# _BALANCE_FUNCTION_COEFF = 0.5
#
#
# class ParenteralSelector:
#     @classmethod
#     def compute(cls, patient, demands, parenterals, excluded_item_ids=None):
#         # TODO: add to DB
#         parenterals["Аминовен 10%"]["Комбинированный"] = 0
#         parenterals["Аминовен инфант 10%"]["Комбинированный"] = 0
#         parenterals["Аминоплазмаль гепа 10%"]["Комбинированный"] = 0
#         parenterals["Глюкоза 10%"]["Комбинированный"] = 0
#         parenterals["Глюкоза 20%"]["Комбинированный"] = 0
#         parenterals["Глюкоза 40%"]["Комбинированный"] = 0
#         parenterals["Глюкоза 5%"]["Комбинированный"] = 0
#         parenterals["Кабивен периферический"]["Комбинированный"] = 1
#         parenterals["Кабивен центральный"]["Комбинированный"] = 1
#         parenterals["Кабивен центральный без жиров"]["Комбинированный"] = 1
#         parenterals["Нефротект 10%"]["Комбинированный"] = 0
#         parenterals["Нутрифлекс 40/80 липид"]["Комбинированный"] = 1
#         parenterals["Нутрифлекс 48/150 липид"]["Комбинированный"] = 1
#         parenterals["Нутрифлекс 70/180 без жиров"]["Комбинированный"] = 1
#         parenterals["Нутрифлекс 70/180 липид"]["Комбинированный"] = 1
#         parenterals["Нутрифлекс 70/240"]["Комбинированный"] = 1
#         parenterals["Оликлиномель N7"]["Комбинированный"] = 1
#         parenterals["Оликлиномель N7 без жиров"]["Комбинированный"] = 1
#         parenterals["СМОФ Кабивен периф. Без жир."]["Комбинированный"] = 1
#         parenterals["СМОФ Кабивен периферический"]["Комбинированный"] = 1
#         parenterals["СМОФ Кабивен центральный"]["Комбинированный"] = 1
#         parenterals["СМОФ Кабивен центральный без жиров"]["Комбинированный"] = 1
#         parenterals["СМОФЛипид 20%"]["Комбинированный"] = 0
#
#         cls.pen_frac = patient["fractions"]["ПЭП"]
#
#         prob = cls._make_balance_problem(demands,
#                                          patient["fractions"]["ПЭП"],
#                                          # patient["Полное восполнение питания"],
#                                          parenterals,
#                                          patient["Масса тела"]["кг"] if patient["Идеальная масса тела"] is None else patient["Идеальная масса тела"]["кг"],
#                                          patient["Возраст"]["лет"],
#                                          patient["Наличие центрального венозного катетера (либо будет установлен в ближайшие 48 часов)"],
#                                          excluded_item_ids)
#         return cls._solve(prob, parenterals)
#
#     @classmethod
#     def _make_balance_problem(cls, demands, f,
#                              parenterals,
#                              m, age_years, cvc, disabled=None):
#         """
#         Ps, Ls, Cs - посчитанные по формулам белок, жиры, углеводы
#         f - полное ли питание (?)
#         pl, pu, ll, lu, cl, cu - нижние и верхние границы для P, L, C
#         m - масса, кг
#         """
#         M = 1e7
#
#         prob = LpProblem("plc-balance", LpMinimize)
#
#         P = LpVariable("P",
#                        lowBound=demands["Белок"]["limits"][0],
#                        upBound=demands["Белок"]["limits"][1])
#         L = LpVariable("L",
#                        lowBound=demands["Жиры"]["limits"][0],
#                        upBound=demands["Жиры"]["limits"][1])
#         C = LpVariable("C",
#                        lowBound=demands["Углеводы"]["limits"][0],
#                        upBound=demands["Углеводы"]["limits"][1])
#
#         # i'th enteral chosen or not
#         xs = LpVariable.dicts("x",
#                               (i for i in range(len(parenterals))),
#                               cat="Binary")
#         ent_doses = LpVariable.dicts("xv",
#                                      (i for i in range(len(parenterals))),
#                                      cat="Continuous",
#                                      lowBound=0)
#
#         f1, f2 = LpVariable("abs_plc_delta"), LpVariable("n_nutritions")
#         f3, f4 = LpVariable("cvk_selection"), LpVariable("total_volume")
#
#         prob += 9 * L + 4 * C >= P * (20 + 5 * 1)
#
#         prob += m * P == lpSum([features["Белок/100мл"] * ent_doses[i]
#                                     for i, (name, features) in enumerate(parenterals.items())])
#         prob += m * L == lpSum([features["Жиры/100мл"] * ent_doses[i]
#                                     for i, (name, features) in enumerate(parenterals.items())])
#         prob += m * C == lpSum([features["Углеводы/100мл"] * ent_doses[i]
#                                     for i, (name, features) in enumerate(parenterals.items())])
#
#         for i in range(len(parenterals)):
#             prob += ent_doses[i] <= xs[i] * M
#
#         for i, (par_name, par) in enumerate(parenterals.items()):
#             if cvc == 0 and par["ЦВК"] == 1:
#                 prob += xs[i] == 0
#             if age_years < par["Возраст"]:
#                 prob += xs[i] == 0
#             if disabled is not None and par_name in disabled:
#                 prob += xs[i] == 0
#
#         prob += lpSum([xs[i]
#                        for i, (par_name, par) in enumerate(parenterals.items())
#                        if par["Комбинированный"] == 1]) <= 1
#
#         #     prob += lpSum([xs[i] * par["Ккал/100мл"]
#         #                    for i, (par_name, par) in enumerate(parenterals.items())]) >= 1
#
#         mp, ml, mc = LpVariable("mp"), LpVariable("ml"), LpVariable("mc")
#
#         # уход от модуля в целевой функции.
#         # (для объяснений - см. примеры с семинаров по Методам Оптимизации)
#         prob += mp >= P - demands["Белок"]["value"]
#         prob += mp >= demands["Белок"]["value"] - P
#         prob += ml >= L - demands["Жиры"]["value"]
#         prob += ml >= demands["Жиры"]["value"] - L
#         prob += mc >= C - demands["Углеводы"]["value"]
#         prob += mc >= demands["Углеводы"]["value"] - C
#
#         prob += lpSum([ent_doses[i] for i in range(len(parenterals))]) >= 1
#
#         prob += f1 == mp + ml + mc
#         prob += f2 == lpSum([xs[i] * (1 + 2 * int("без жиров" in list(parenterals.keys())[i]))
#                              for i in range(len(parenterals))])
#         prob += f3 == -cvc * lpSum([xs[i] * par["ЦВК"]
#                                     for i, (par_name, par) in enumerate(parenterals.items())])
#         prob += f4 == lpSum([ent_doses[i] for i in range(len(parenterals))])
#
#         c1, c2, c3, c4 = 10, 5, 1, 0
#
#         prob += c1 * f1 + c2 * f2 + c3 * f3 + c4 * f4
#
#         return prob
#
#     @classmethod
#     def _solve(cls, lp_prob, parenterals):
#         lp_prob.solve()
#
#         if LpStatus[lp_prob.status] != "Optimal":
#             raise Exception(f"LP Status: {LpStatus[lp_prob.status]}")
#             return None
#
#         # print({k: v.value() for k,v in lp_prob.variablesDict().items()})
#
#         prob_vars = lp_prob.variablesDict()
#         out_demands = {key: prob_vars[key].value()
#                        for key in ["P", "L", "C"]}
#         out_parenterals = {}
#         for i in range(len(parenterals)):
#             if prob_vars[f"x_{i}"].value() == 1:
#                 val = prob_vars[f'xv_{i}'].value() * 100 * cls.pen_frac
#                 val = round(val / 10) * 10
#                 out_parenterals[list(parenterals.keys())[i]] = val
#
#         return out_demands, out_parenterals


from pulp import LpProblem, LpVariable, LpStatus, LpMinimize, lpSum

_BALANCE_FUNCTION_COEFF = 0.5


class ParenteralSelector:
    @classmethod
    def compute(cls, patient, demands, parenterals, excluded_item_ids=None, full_problem=True):
        # TODO: add to DB
        parenterals["Аминовен 10%"]["Комбинированный"] = 0
        parenterals["Аминовен инфант 10%"]["Комбинированный"] = 0
        parenterals["Аминоплазмаль гепа 10%"]["Комбинированный"] = 0
        parenterals["Глюкоза 10%"]["Комбинированный"] = 0
        parenterals["Глюкоза 20%"]["Комбинированный"] = 0
        parenterals["Глюкоза 40%"]["Комбинированный"] = 0
        parenterals["Глюкоза 5%"]["Комбинированный"] = 0
        parenterals["Кабивен периферический"]["Комбинированный"] = 1
        parenterals["Кабивен центральный"]["Комбинированный"] = 1
        parenterals["Кабивен центральный без жиров"]["Комбинированный"] = 1
        parenterals["Нефротект 10%"]["Комбинированный"] = 0
        parenterals["Нутрифлекс 40/80 липид"]["Комбинированный"] = 1
        parenterals["Нутрифлекс 48/150 липид"]["Комбинированный"] = 1
        parenterals["Нутрифлекс 70/180 без жиров"]["Комбинированный"] = 1
        parenterals["Нутрифлекс 70/180 липид"]["Комбинированный"] = 1
        parenterals["Нутрифлекс 70/240"]["Комбинированный"] = 1
        parenterals["Оликлиномель N7"]["Комбинированный"] = 1
        parenterals["Оликлиномель N7 без жиров"]["Комбинированный"] = 1
        parenterals["СМОФ Кабивен периф. Без жир."]["Комбинированный"] = 1
        parenterals["СМОФ Кабивен периферический"]["Комбинированный"] = 1
        parenterals["СМОФ Кабивен центральный"]["Комбинированный"] = 1
        parenterals["СМОФ Кабивен центральный без жиров"]["Комбинированный"] = 1
        parenterals["СМОФЛипид 20%"]["Комбинированный"] = 0
        parenterals["Аминоплазмаль гепа 10%"]["Гепа"] = 1
        parenterals["Нефротект 10%"]["Нефро"] = 1

        cls.pen_frac = patient["fractions"]["ПЭП"]
        cls.anamnesis = {k: patient[k] for k in
                         ["Острое повреждение почек", "Хроническая болезнь почек", "Острая печеночная недостаточность"]}

        prob = cls._make_balance_problem(demands,
                                         patient["fractions"]["ПЭП"],
                                         # patient["Полное восполнение питания"],
                                         parenterals,
                                         patient["Масса тела"]["кг"] if patient["Идеальная масса тела"] is None else
                                         patient["Идеальная масса тела"]["кг"],
                                         patient["Возраст"]["лет"],
                                         patient[
                                             "Наличие центрального венозного катетера (либо будет установлен в ближайшие 48 часов)"],
                                         excluded_item_ids, full_problem)
        return cls._solve(prob, parenterals)

    @classmethod
    def _make_balance_problem(cls, demands, f,
                              parenterals,
                              m, age_years, cvc, disabled=None, full_problem=True):
        """
        Ps, Ls, Cs - посчитанные по формулам белок, жиры, углеводы
        f - полное ли питание (?)
        pl, pu, ll, lu, cl, cu - нижние и верхние границы для P, L, C
        m - масса, кг
        """

        M = 1e7
        Mm = 1e-1

        prob = LpProblem("parenteral-selection", LpMinimize)

        P = LpVariable("P",
                       lowBound=demands["Белок"]["limits"][0],
                       upBound=demands["Белок"]["limits"][1])
        L = LpVariable("L",
                       lowBound=demands["Жиры"]["limits"][0],
                       upBound=demands["Жиры"]["limits"][1])
        C = LpVariable("C",
                       lowBound=demands["Углеводы"]["limits"][0],
                       upBound=demands["Углеводы"]["limits"][1])

        # i'th parenteral chosen or not
        xs = LpVariable.dicts("x",
                              (i for i in range(len(parenterals))),
                              cat="Binary")
        ent_doses = LpVariable.dicts("xv",
                                     (i for i in range(len(parenterals))),
                                     cat="Continuous",
                                     lowBound=0)

        prob += 9 * L + 4 * C >= P * (20 + 5 * f)

        for i, (par_name, par) in enumerate(parenterals.items()):
            prob += ent_doses[i] <= xs[i] * M
            prob += ent_doses[i] >= Mm * xs[i]

            if cvc == 0 and par["ЦВК"] == 1:
                prob += xs[i] == 0
            if age_years < par["Возраст"]:
                prob += xs[i] == 0
            if disabled is not None and par_name in disabled:
                prob += xs[i] == 0

        mp, ml, mc = LpVariable("mp"), LpVariable("ml"), LpVariable("mc")
        f1, f2 = LpVariable("abs_plc_delta"), LpVariable("n_nutritions")
        f3, f4 = LpVariable("cvk_selection"), LpVariable("total_volume")

        # уход от модуля в целевой функции.
        # (для объяснений - см. примеры с семинаров по Методам Оптимизации)
        prob += mp >= P - demands["Белок"]["value"]
        prob += mp >= demands["Белок"]["value"] - P
        prob += ml >= L - demands["Жиры"]["value"]
        prob += ml >= demands["Жиры"]["value"] - L
        prob += mc >= C - demands["Углеводы"]["value"]
        prob += mc >= demands["Углеводы"]["value"] - C

        prob += f1 == mp + ml + mc

        theta_inds = [i
                      for i, (par, par_features) in enumerate(parenterals.items())
                      if par_features["Белок/100мл"] > 0]
        prob += lpSum([xs[i] for i in theta_inds]) == 1

        aki, cki, ali = list(cls.anamnesis.values())

        prob += f2 == lpSum([xs[i] * (
                    1 + 2 * ("без жиров" in parenterals) - (100 + 100 * ali * (aki + cki)) * features.get("Гепа",
                                                                                                          0) * ali - 100 * features.get(
                "Нефро", 0) * (aki + cki))
                             for i, (par_name, features) in enumerate(parenterals.items())
                             if i in theta_inds])

        prob += m * P == lpSum([features["Белок/100мл"] * ent_doses[i]
                                for i, (name, features) in enumerate(parenterals.items())])
        prob += m * L == lpSum([features["Жиры/100мл"] * ent_doses[i]
                                for i, (name, features) in enumerate(parenterals.items())])
        prob += m * C == lpSum([features["Углеводы/100мл"] * ent_doses[i]
                                for i, (name, features) in enumerate(parenterals.items())])

        g = LpVariable("can_select_nocomb_nogluk",
                       cat="Binary")

        comb_inds = [i
                     for i, (par_name, features) in enumerate(parenterals.items())
                     if features.get("Комбинированный") == 1]
        prob += lpSum([xs[i]
                       for i in comb_inds]) <= 1
        prob += lpSum([xs[i]
                       for i in comb_inds]) >= 1 - g
        nocomb_nogluk_inds = [i
                              for i, (par_name, features) in enumerate(parenterals.items())
                              if i not in comb_inds and (features["Белок/100мл"] > 0 or features["Жиры/100мл"] > 0)]
        prob += lpSum([xs[i]
                       for i in nocomb_nogluk_inds]) <= M * g

        prob += f2 + f1 + g

        return prob

    @classmethod
    def _solve(cls, lp_prob, parenterals):
        lp_prob.solve()

        if LpStatus[lp_prob.status] != "Optimal":
            raise Exception(f"LP Status: {LpStatus[lp_prob.status]}")
            return None

        # print({k: v.value() for k,v in lp_prob.variablesDict().items()})

        prob_vars = lp_prob.variablesDict()
        out_demands = {key: prob_vars[key].value()
                       for key in ["P", "L", "C"]}
        out_parenterals = {}
        for i in range(len(parenterals)):
            if prob_vars[f"x_{i}"].value() == 1:
                val = prob_vars[f'xv_{i}'].value() * 100 * cls.pen_frac
                val = round(val / 10) * 10
                out_parenterals[list(parenterals.keys())[i]] = val

        return out_demands, out_parenterals