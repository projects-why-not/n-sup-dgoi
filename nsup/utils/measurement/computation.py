# from .bmi import BMI
# from .zscore import ZScore
# from .nutritive_status import NormalNutritiveStatus, LightProteinCalorieDeficiency, MediumProteinCalorieDeficiency, \
#     AcuteProteinCalorieDeficiency, Overweight, Obesity1, Obesity2, Obesity3, ObesitySevere
# from .syndrome import GFR, ALF, AKI, VisceralPoolProteinDeficiency, AcutePancreatite, Cholestasis, RefeedingRisk
# from .extra import NoProteinKCal, Toxicity
# from .age import Ager
# from .perfect_mass import PerfectMass


class DerivedParameterComputation:
    @classmethod
    def compute(cls, db_wrapper, **kwargs):
        out_dict = kwargs

        # out_dict[Ager.name] = Ager.compute(**kwargs)

        # for analysis in [row[0] for row in db_wrapper.wrapper._select("SELECT DISTINCT name FROM clinical_limits")]:
        #     out_dict["Min*" + analysis], out_dict["Max*" + analysis] = db_wrapper.get_clinical_limits(analysis,
        #                                                                                               out_dict["Пол"],
        #                                                                                               out_dict["Возраст"])

        computation_params = db_wrapper.get_derived_parameters()

        parenterals = db_wrapper.get_nutrition_features(False)
        enterals = db_wrapper.get_nutrition_features(True)

        out_dict["ПЭП"] = parenterals
        out_dict["ЭП"] = enterals

        # computation_params = [
        #     # (Ager, {}, None),
        #     (BMI, {}, None),
        #     (ZScore, {"z-score-key": "Рост"}, "z-score роста"),
        #     (ZScore, {"z-score-key": "Масса тела"}, "z-score массы тела"),
        #     (ZScore, {"z-score-key": BMI.name}, "z-score ИМТ"),
        #     (NormalNutritiveStatus, {}, None),
        #     (LightProteinCalorieDeficiency, {}, None),
        #     (MediumProteinCalorieDeficiency, {}, None),
        #     (AcuteProteinCalorieDeficiency, {}, None),
        #     (Overweight, {}, None),
        #     (Obesity1, {}, None),
        #     (Obesity2, {}, None),
        #     (Obesity3, {}, None),
        #     (ObesitySevere, {}, None),
        #     (VisceralPoolProteinDeficiency, {}, None),
        #     (NoProteinKCal, {"db_wrapper": db_wrapper}, None),
        #     (GFR, {}, None),
        #     (ALF, {}, None),
        #     (ARI, {}, None),
        #     (Cholestasis, {}, None),
        #     (AcutePancreatite, {}, None),
        #     (Toxicity, {}, None),
        #     (RefeedingRisk, {}, None)
        # ]

        out_dict["Производные параметры"] = []
        for param_data in computation_params:
            param_class = eval(param_data["class"])
            param_name = param_data["name"]
            if param_name == "Риск рефидинг-синдрома":
                # MARK: go on. Should be computed later
                continue

            if param_data["class"] == "NoProteinKCal":
                app_dict = {"db_wrapper": db_wrapper}
            else:
                app_dict = param_data["in_appendix"]
                # FIXME: move to db!
                app_dict = {k.replace("-", "_"): v for k,v in app_dict.items()}

            out_dict[param_class.name if param_name is None else param_name] = param_class.compute(**kwargs,
                                                                                                   **app_dict)
            out_dict["Производные параметры"] = out_dict["Производные параметры"] + [param_class.name if param_name is None else param_name]
        return out_dict
