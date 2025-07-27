from ..utils.measurement import DerivedParameterComputation
from ..utils.age import Age
from .parameter_imputation import ParameterImputer
# from ..utils.measurement.bmi import BMI
# from ..utils.measurement.zscore import ZScore
# from ..utils.measurement.nutritive_status import NormalNutritiveStatus, LightProteinCalorieDeficiency, MediumProteinCalorieDeficiency, \
#     AcuteProteinCalorieDeficiency, Overweight, Obesity1, Obesity2, Obesity3, ObesitySevere
# from ..utils.measurement.syndrome import GFR, ALF, AKI, VisceralPoolProteinDeficiency, AcutePancreatite, Cholestasis, RefeedingRisk
# from ..utils.measurement.extra import NoProteinKCal, Toxicity
# # from ..utils.measurement.age import Ager
from tqdm import tqdm


class PatientInfo:
    def __init__(self, data_dict, db_wrapper=None):
        self.id = data_dict["ID"]

        data_dict["Возраст"] = Age(data_dict["Дата консультации"],
                                   data_dict["Дата рождения"])

        if db_wrapper is not None:
            parenterals = db_wrapper.get_nutrition_features(enteral=False)
            data_options = ParameterImputer.impute(data_dict, db_wrapper)
        else:
            data_options = [data_dict]

        for i, d_dict in tqdm(enumerate(data_options)):
            if db_wrapper is not None:
                # parenterals = db_wrapper.get_nutrition_features(enteral=False)
                for k, v in data_options[i]["Тек*Растворы ПЭП"].items():
                    parenteral_name = v["Название раствора для ПЭП"]
                    if parenteral_name is None or len(parenteral_name) == 0:
                        continue
                    for fea, val in parenterals[parenteral_name].items():
                        data_options[i]["Тек*Растворы ПЭП"][k][fea] = val

                data_options[i] = DerivedParameterComputation.compute(db_wrapper, **d_dict)

            # FIXME!!
            data_options[i]["Частичная нутритивная поддержка"] = 0
            data_options[i]["Полное восполнение питания"] = 1

        self.data = data_options
