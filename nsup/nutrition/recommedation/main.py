from ..primitive.protein import ProteinDerivation
from ..primitive.lipid import LipidDerivation
from ..primitive.carbohydrate import CarbohydrateDerivation
from ..primitive.energy import EnergyDerivation
from ...utils.measurement.syndrome import RefeedingRisk
from ...utils.measurement.enteral_tagging import EnteralTagging
from ...utils.measurement.nutrition_type_fraction import NutritionTypeFractions
from ...utils.value.conversion import UnitConverter
from .recommendation_set import RecommendationSet
from ..selection import EnteralSelector, ParenteralSelector


class NutritionRecommender:
    _classes = {"Белок": ProteinDerivation,
                "Жиры": LipidDerivation,
                "Углеводы": CarbohydrateDerivation,
                "ККал": EnergyDerivation}

    def __init__(self, patient, db_wrapper):
        self.patient = patient
        self.db_wrapper = db_wrapper

    def get_recommendations(self):
        recommendations = [self._get_rec_set(d_dict) for d_dict in self.patient.data]
        for i in range(len(recommendations)):
            recommendations[i]["id"] = i
        return recommendations

    def _get_rec_set(self, data_dict):
        due_demands = self._compute_due_demands(data_dict)

        # fractions = NutritionTypeFractions.get_from_form(**data_dict)
        # data_dict["fractions"] = fractions
        recom_set = {}

        recom_set["ПЭП"] = self._get_pen_recommendations(data_dict)

        recom_set["ЭП"] = self._get_en_recommendations(data_dict, due_demands)

        energy_basic = EnergyDerivation.energy_basic_f(data_dict["Возраст"]["лет"],
                                                       int(data_dict["Пол"] == "Мужской"),
                                                       data_dict["Масса тела"]["кг"],
                                                       data_dict["Рост"]["м"])

        recom_set["Энергия основного обмена"] = energy_basic
        recom_set["due_demands"]["ЭП"] = {k: recom_set["due_demands"]["ЭП"][k] for k in
                                          ["Энергия основного обмена", "ККал", "Белок", "Жиры", "Углеводы"]}

        return recom_set

    def _compute_due_demands(self, data_dict):
        due_demands = {k + "_due": _class.compute(data_dict, due_only=True)
                       for k, _class in self._classes.items()}
        refeeding_risk = RefeedingRisk.compute(**data_dict, **due_demands)
        if not data_dict["Учитывать ли риск рефидинг-синдрома"]:
            data_dict[RefeedingRisk.name] = 0
        else:
            data_dict[RefeedingRisk.name] = refeeding_risk
        data_dict["Производные параметры"] = data_dict["Производные параметры"] + [RefeedingRisk.name]
        return due_demands

    def _get_pen_recommendations(self, data_dict):
        if int(data_dict["only_en"]):
            return {"nutrition": {},
                    "demands": {},
                    "due_demands": {},
                    "full_problem": "N/A"}

        demands = {k: dict(zip(["value", "limits", "due"],
                               _class.compute(data_dict)))
                   for k, _class in self._classes.items()
                   if k != "ККал"}

        return {"demands": demands}

    def _get_en_recommendations(self, data_dict, due_demands):
        def _get_en_subrecommendations(sipping):
            en_due_demands = {"ККал": due_demands["ККал_due"],
                              "Белок": EnteralSelector._p_en_f(data_dict["Возраст"]["лет"],
                                                               due_demands["ККал_due"]),
                              "Жиры": EnteralSelector._l_en_f(data_dict["Возраст"]["лет"],
                                                              due_demands["ККал_due"]),
                              "Углеводы": EnteralSelector._c_en_f(data_dict["Возраст"]["лет"],
                                                                  due_demands["ККал_due"])
                              }
            data_dict["Производные параметры"] = data_dict["Производные параметры"] + ["Возраст"]

            return {"due_demands": en_due_demands}

        if int(data_dict["only_pen"]):
            return {"сипинг": {},
                    "зонд": {}}

        # data_dict[EnteralTagging.name] = EnteralTagging.compute(**data_dict)
        #
        # enteral_tags = self.db_wrapper.get_nutrition_tags(enteral=True)

        res = {}
        for sip in [False, True]:
            res["сипинг" if not sip else "зонд"] = _get_en_subrecommendations(sip)

        res["enteral_tags"] = EnteralTagging.compute(**data_dict)

        return res
