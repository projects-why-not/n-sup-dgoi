from .db import DBWrapper
from ..age import Age


class DBProvider:
    def __init__(self, db_name, db_user, db_passwd, db_host="localhost", db_port=3306):
        self.wrapper = DBWrapper(db_name, db_user, db_passwd, db_host, db_port)

    def get_data_config(self):
        def format_field_options(field):
            if field["type"] == "datalist" and ("ЭП" in field["label"]):
                opts = self.wrapper.get_nutrition("ПЭП" not in field["label"])
            else:
                opts = self.wrapper.get_selection_options(field["id"], field["label"])
            formatted_opts = [dict(zip(["id", "name"], opt)) for opt in opts]
            return formatted_opts

        def format_field_block(field):
            subl_fields = self.wrapper.get_subblock_fields(field["id"])
            subitems = [dict(zip(["id", "label", "type", "dtype", "units", "onChangeMethod", "onChange", "defaultValue", "is_required", "attributes"], row)) for row in subl_fields]
            for i, subfield in enumerate(subitems):
                if subfield["type"] in ["select", "datalist", "switch", "radio"]:
                    subitems[i]["options"] = format_field_options(subfield)
                elif subfield["type"] in ["vstack", "hstack"]:
                    subitems[i]["options"] = format_field_block(subfield)

            return subitems

        blocks = self.wrapper.get_blocks()
        # req_data = {bl_name[1] : [] for bl_name in blocks }
        req_data = {}
        for bl in blocks:
            block_key = (bl[0], bl[1])
            req_data[block_key] = []
            bl_fields = self.wrapper.get_block_fields(bl[0])

            req_data[block_key] = [dict(zip(["id", "label", "type", "dtype", "units", "onChangeMethod", "onChange", "defaultValue", "is_required", "attributes"], row)) for row in bl_fields]
            for i, field in enumerate(req_data[block_key]):
                if field["type"] in ["select", "datalist", "switch", "radio"]:
                    # opts = self.wrapper.get_selection_options(field["id"], field["label"])
                    req_data[block_key][i]["options"] = format_field_options(field) # [
                    #      dict(zip(["id", "name"], opt)) # [translit(opt[1], "ru", reversed=True), opt[1]]))
                    #      for opt in opts]
                elif field["type"] in ["vstack", "hstack"]:
                    req_data[block_key][i]["options"] = format_field_block(field)

        return req_data

    def get_nutrition_features(self, enteral):
        feature_db_fetch = self.wrapper.get_nutrition_key_features(enteral)
        out_dict = {}
        for row in feature_db_fetch:
            if row[0] not in out_dict:
                out_dict[row[0]] = {}
            try:
                out_dict[row[0]][row[1]] = float(row[2])
            except ValueError:
                out_dict[row[0]][row[1]] = row[2]

        return out_dict

    def get_clinical_limits(self, analysis_name, sex, age):
        all_limits = self.wrapper.get_clinical_limits(analysis_name, sex)

        age_keys = {"D": "дней", "M": "мес", "W": "нед", "Y": "лет"}
        for option in all_limits:
            low_age = Age({age_keys[option[5]]: option[4]})
            high_age = Age({age_keys[option[7]]: option[6]})

            print()

            if low_age <= age < high_age:
                return option[-2:]

    def get_derived_parameters(self):
        derived_params = self.wrapper.get_derived_parameters()
        references = self.wrapper.get_derived_params_reference()
        appendices = self.wrapper.get_derived_params_appendices()
        out_params = []
        for (_id, name, comp_class) in derived_params:
            loc_dict = {"name": name,
                        "class": comp_class,
                        "reference": [row[1] if row[1] is not None else row[2]
                                      for row in references if row[0] == _id],
                        "in_appendix": {row[1]: row[2]
                                        for row in appendices if row[0] == _id}
                        }
            out_params += [loc_dict]
        return out_params

    def get_nutrition_tags(self, enteral=None):
        data = self.wrapper.get_nutrition_tags(enteral)
        tags = {}
        for (nutr_name, tag) in data:
            tags[nutr_name] = tags.get(nutr_name, []) + [tag]
        return tags
