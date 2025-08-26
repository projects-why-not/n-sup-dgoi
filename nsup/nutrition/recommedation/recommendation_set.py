from ...utils.measurement.enteral_tagging import EnteralTagging
import numpy as np


class RecommendationSet:
    value_alias = {"P": "Белок",
                   "C": "Углеводы",
                   "L": "Жиры",
                   "E": "ККал"}

    def __init__(self, data_dict):
        self._derived_params = {k: data_dict[k]
                                for k in data_dict["Производные параметры"]}
        self._recommendations = {"ПЭП": {},
                                 "ЭП": {}}
        self._mass = data_dict["Масса тела"]["кг"]
        self._fractions = data_dict["fractions"]

    def __getitem__(self, item):
        return self._recommendations.get(item, None)

    def __setitem__(self, key, value):
        self._recommendations[key] = value

    def to_dict(self):
        out_dict = {"Производные параметры": {k: v["кг"] if (k == "Идеальная масса тела" and v is not None) else v
                                              for k,v in self._derived_params.items()
                                              if k not in ["Возраст"]},
                    "Доли": {k: f"{v * 100} %" for k,v in self._fractions.items()}}
        for k in self._fractions.keys():
            out_dict[k] = {"Назначения": {item: f"{features['dose']} мл"
                                          for item, features in self._recommendations[k]["nutrition"].items()
                                          if features['dose'] > 0},
                           "Потребности": self._recommendations[k]["demands"]}
        return out_dict

    def to_vector(self):
        en_sipping_data = self._en_list_for_compare_f(self._recommendations["сипинг"])
        en_stoma_data = self._en_list_for_compare_f(self._recommendations["зонд"])
        pen_data = self._pen_list_for_compare_f(self._recommendations["ПЭП"])

        return en_sipping_data + en_stoma_data + pen_data

    def __call__(self, *args, **kwargs):
        return self.to_dict()

    def _en_list_for_compare_f(self, item: dict) -> list:
        """
        Функция для ЭП
        Составление списка из числовых значений - координат в пространстве выдач для последующего сравнения.

        :param item: словарь с данными о смеси: объем смеси для приема по результатам выдачи; ккал на 100 мл смеси, белок на 100 мл, жиры на 100 мл, углеводы на 100 мл - из базы по смеси
        :param patient: словарь с результатами расчетов energy_due, p_en_f, l_en_f, c_en_f для пациента
        :param tags_presence: словарь с парами тег:его значение для данной смеси из базы данных (без учета вероятности тега для пациента!!!)
        :return: список части координат (для сипинга или зонда)
        """

        if len(item["nutrition"]) == 0:
            return [0] * (4 + len(EnteralTagging.weights))

        item, due_demands = list(item["nutrition"].values())[0], item["demands"]

        values_list = []

        for value in sorted(list(due_demands.keys())):
            values_list.append((item['dose'] / 100 * item["features"][f"{value}/100мл"]) / due_demands[value])

        reverse_trans = {v: k for k,v in EnteralTagging.trans.items()}
        for tag in list(item["tags"]):
            values_list.append(EnteralTagging.tag_hierarchy_f(reverse_trans[tag], item["tags"][tag]))

        return values_list

    def _pen_list_for_compare_f(self, item: dict) -> list:
        """
        Функция для ПЭП
        Составление списка из числовых значений - координат в пространстве выдач для последующего сравнения.


        ! Ключи в обоих словарях одинаковые !
        :param item: словарь с данными о ПЭП: сколько белка, жиров, углеводов на кг ассы тела пациента содержится в ПЭП
        :param patient: словарь с результатами расчетов protein_due, lipids_due, carbogydrate_gue для пациента
        :return: список части координат (для ПЭП)
        """

        if len(item["nutrition"]) == 0:
            return [0] * 3

        values_list = []
        for _, nutr in item["nutrition"].items():
            for value in sorted(list(item["demands"].keys())):
                if value == "ККал_due":
                    continue
                values_list.append((nutr["features"][f"{value.split('_')[0]}/100мл"] / 100 * nutr["dose"] / self._mass) / item["demands"][value])
        values_list = np.array(values_list).reshape((-1, 3)).sum(axis=0).tolist()

        return values_list



