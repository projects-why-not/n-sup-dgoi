import numpy as np
from copy import deepcopy
from ..utils.age import Age


class ParameterImputer:
    @classmethod
    def impute(cls, data_dict, db_wrapper):
        # FIXME: access to protected field!
        params_to_impute = [row[0] for row in db_wrapper.wrapper._select("SELECT DISTINCT name FROM clinical_limits")]
        # print(params_to_impute)
        # input("goon?")
        for analysis in params_to_impute:
            data_dict["Min*" + analysis], data_dict["Max*" + analysis] = db_wrapper.get_clinical_limits(analysis,
                                                                                                        data_dict["Пол"],
                                                                                                        data_dict["Возраст"])
        data_variations = {}
        for analysis in params_to_impute:
            impute_func, options, ref_param = cls.get_options(analysis)
            if impute_func is None:
                continue
            tgt_param = analysis  # if ref_param is None else ref_param

            # TODO: add date check!
            if data_dict[tgt_param][tgt_param] != -1:
                if tgt_param != "Креатинин":
                    bounds = [data_dict.get("Min*" + tgt_param, None),
                              data_dict.get("Max*" + tgt_param, None)]
                else:
                    bounds = [((data_dict["Пол"] == "Женский") * 0.368 +
                               (data_dict["Пол"] == "Мужской") * (0.368 + 0.045 * (data_dict["Возраст"] > Age(12,0)))) *
                              data_dict["Рост"]["см"] / (88.4 * 60),
                              None]
                data_dict[analysis + "_imputed"] = impute_func(data_dict[tgt_param],
                                                               *bounds)
            else:
                # TODO: fix imputation!
                # data_variations[analysis] = options
                data_dict[tgt_param][tgt_param] = (data_dict["Max*" + tgt_param] + data_dict["Min*" + tgt_param]) / 2

        # imp_variations = np.vstack(np.meshgrid(*list(data_variations.values()))).reshape((len(data_variations), -1)).T
        # if imp_variations.shape[0] == 0:
        #     return [data_dict]

        # FIXME: remove line
        return [data_dict]

        # variations = [deepcopy(data_dict)
        #               for _ in range(imp_variations.shape[0])]
        # var_keys = list(data_variations.keys())
        # for k, imp_set in enumerate(imp_variations):
        #     for i, key in enumerate(var_keys):
        #         variations[k][key + "_imputed"] = imp_set[i]
        #
        # # TODO: find unique
        # return variations

    @classmethod
    def get_options(cls, param_name):
        # TODO: add to DB
        options = {"Лейкоциты": (lambda x, l, u: int(x < 1000),
                                 (0,1), None),
                   "Тромбоциты": (lambda x, l, u: int(x < 40),
                                 (0,1), None),
                   "Глюкоза": (lambda x, l, u: int(x > 8),
                               (0,1), None),
                   "АЛТ": (lambda x, l, u: int(x > u),
                           (0,1), None),
                   "АСТ": (lambda x, l, u: int(x > u),
                           (0, 1), None),
                   "Билирубин общий": (lambda x, l, u: int(x > u),
                                       (0, 1), None),
                   "Билирубин прямой": (lambda x, l, u: int(x > u),
                                       (0, 1), None),
                   "Мочевина": (lambda x, l, u: int(x > u),
                                (0, 1), None),
                   "Креатинин": (lambda x, l, u: -1 * int(x <= l),
                                 (-1, 0), None),
                   "Триглицериды": (lambda x, l, u: -1 if x < 3 else 1 if x > 4 else 0,
                                    (-1, 0, 1), None),
                   "Амилаза": (lambda x, l, u: int(x > 3 * u),
                                (0, 1), None),
                   "Липаза": (lambda x, l, u: int(x > 3 * u),
                                (0, 1), None),
                   "Цистатин C": (lambda x, l, u: int(x > u),
                                  (0, 1), None),
                   "Альбумин": (lambda x, l, u: int(x < l),
                                (-1, 0), None),
                   "Лактат": (lambda x, l, u: int(x > u),
                              (0, 1), None),
                   "Щелочная фосфатаза": (lambda x, l, u: int(x > 1.5 * u),
                                          (0, 1), None),
                   "Гамма-глутамилтрансфераза": (lambda x, l, u: int(x > 3 * u),
                                                 (0, 1), None),
                   "Калий": (lambda x, l, u: -1 if x < 0.5 * l else 1 if x >= 0.75 * l else 0,
                             (-1, 0, 1), None),
                   "Фосфор неорганический": (lambda x, l, u: -1 if x < 0.5 * l else 1 if x >= 0.75 * l else 0,
                                             (-1, 0, 1), None),
                   "Магний общий": (lambda x, l, u: -1 if x < 0.5 * l else 1 if x >= 0.75 * l else 0,
                                    (-1, 0, 1), None),
                   }
        return options.get(param_name, (None, None, None))
