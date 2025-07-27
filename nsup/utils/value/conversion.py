from .unit import units


class UnitConverter:
    units = units
    unit_classes = {u: utype
                    for utype, vs in units.items()
                    for u in vs}

    @classmethod
    def convert(cls, value, src_unit, tgt_unit):
        assert src_unit in cls.unit_classes and tgt_unit in cls.unit_classes, f"{src_unit} or {tgt_unit} are missing in {cls.unit_classes}"
        assert cls.unit_classes[src_unit] == cls.unit_classes[tgt_unit]
        unit_class = cls.unit_classes[src_unit]
        return value / cls.units[unit_class][src_unit] * cls.units[unit_class][tgt_unit]

    @classmethod
    def nutrition_to_features(cls, nutr_set, av_nutritions, is_enteral):
        tgt_features = ["Белок/100мл", "Жиры/100мл", "Углеводы/100мл"]
        if is_enteral:
            tgt_features += ["ККал/100мл"]

        res = {k.split('/')[0]: 0 for k in tgt_features}

        # raise Exception(f"{nutr_set}")

        for nutr, features in nutr_set.items():
            # raise Exception(f"{features}")
            for tgt_f in res:
                res[tgt_f] = res[tgt_f] + features["features"][tgt_f + "/100мл"] * (features["dose"] / 100)
        return res
