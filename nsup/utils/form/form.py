import json
from time import time
from datetime import date, datetime
from random import random
from ..value import Value, str_is_unit, Analysis


def form_to_json(form_dict, field_mapping):
    out_dict = form_dict
    fname = str(time()) + str(random()).split(".")[1] + ".json"
    # TODO


def file_to_dict(contents):
    def str_to_genitive(s):
        pts = s.split()
        if pts[0][-1] == "а":
            pts[0] = pts[0][:-1] + "ы"
        elif pts[0][-1] == "т":
            pts[0] = pts[0] + "а"
        return " ".join(pts)

    def _unpack_analysis_items(form_dict):
        form_dict = form_dict
        cur_date = form_dict["Дата консультации"]
        for k, v in form_dict.items():
            if type(v) is not dict:
                continue
            if k not in v:
                continue

            form_dict[k] = Analysis(v)

            # TODO: интервал доверия к анализам

            # FIXME: default values for analyses
            # form_dict[k][v + "-raw"] = form_dict[k][v]

            # form_dict[k][v] = form_dict[k][v]

        return form_dict

    # contents = up_file.read()

    out_dict = json.loads(contents)

    # MARK: datetime processing
    for k, v in out_dict.items():
        if v == "N/A":
            out_dict[k] = None
        elif type(v) is str and v.find("datetime") == 0:
            out_dict[k] = datetime.strptime(v, "datetime.date(%Y, %m, %d)").date()
        elif type(v) is dict and "Дата анализа" in v.keys():
            out_dict[k]["Дата анализа"] = datetime.strptime(v["Дата анализа"],
                                                            "datetime.date(%Y, %m, %d)").date()

    out_dict = _unpack_analysis_items(out_dict)

    for f_name in ["Масса тела", "Рост"]:
        unit_field_name = "единицы измерения " + str_to_genitive(f_name).lower()
        f_value = Value(out_dict[f_name], out_dict[unit_field_name])
        out_dict[f_name] = f_value

    # out_dict["only_en"] = out_dict["only_en"]
    # out_dict["only_pen"] = out_dict["only_pen"]

    print(out_dict)

    return out_dict


def form_to_dict(form_dict, field_mapping):
    def _unpack_analysis_items(form_dict):
        form_dict = form_dict
        cur_date = form_dict["Дата консультации"]
        for k, v in form_dict.items():
            if type(v) is not dict:
                continue
            if k not in v:
                continue

            form_dict[k] = Analysis(v)

            # TODO: интервал доверия к анализам

            # FIXME: default values for analyses
            # form_dict[k][v + "-raw"] = form_dict[k][v]

            # form_dict[k][v] = form_dict[k][v]

        return form_dict

    def convert_value(val, _type=None, _dtype=None):
        if val == "N/A":
            return val
        if val in ["да", "нет"]:
            return val == "да"
        if str_is_unit(val):
            return val

        assert _type is not None

        if _type in ["select", "radio"]:
            return val
        elif _type == "datalist":
            return val
        elif _type == "input":
            assert _dtype is not None

            if _dtype == "number":
                return float(val.replace(",", ".")) if len(val) > 0 else None
            elif _dtype == "date":
                return date(*[int(pt) for pt in val.split("-")]) if len(val) > 0 else None
            return val
        else:
            raise ValueError(f"Wrong field type provided: {[val, _type, _dtype]}!")

    def str_to_genitive(s):
        pts = s.split()
        if pts[0][-1] == "а":
            pts[0] = pts[0][:-1] + "ы"
        elif pts[0][-1] == "т":
            pts[0] = pts[0] + "а"
        return " ".join(pts)

    def parse_form_field(field_form_id, field):
        # TODO: format conversion
        f_name = field["label"]
        if field_form_id not in list(form_dict.keys()):
            if field["type"] == "radio":
                raise ValueError("All Radio buttons must be chosen!")
            elif field["type"] == "switch":
                return f_name, convert_value(field["options"][0]["name"])
            elif field["type"] in ["vstack", "hstack"]:
                if f_name in ["Смеси ЭП", "Растворы ПЭП"] and field_form_id[0] == '6':
                    f_name = "Тек*" + f_name

                if field["type"] == "vstack" and ("Смеси ЭП" in f_name or "Растворы ПЭП" in f_name):
                    cnt = 1
                    res = {}
                    child_id = field_form_id + "_" + str(field["options"][0]["id"])

                    while len([1 for k in form_dict if child_id.replace("*1*", f"*{cnt}*") in k]) > 0:
                        loc_res = parse_form_field(child_id.replace("*1*", f"*{cnt}*"), field["options"][0])
                        res[loc_res[0] + f" {cnt}"] = loc_res[1]
                        cnt += 1
                    return f_name, res

                res = f_name, {parse_form_field(field_form_id + "_" + str(child["id"]), child)[0]:
                                   parse_form_field(field_form_id + "_" + str(child["id"]), child)[1]
                               for child in field["options"]}
                return res
            elif field["type"] == "button":
                return None, None
            elif f_name in ["Дата постановки стомы/зонда",
                            "Для сухих смесей: укажите разведение"]:
                return f_name, "N/A"
            elif f_name in ["Доля парентерального питания",
                            "Доля энтерального питания (сипинг)",
                            "Доля энтерального питания (зонд/стома)"]:
                return f_name, 0
            elif f_name in ["ID", "Основной диагноз"]:
                return f_name, None
            elif f_name == "Cколько часов в сутках доступно для потенциального ПЭП":
                return f_name, 24
            else:
                return f_name, None
                # raise Exception(f"How can it be?? {field['type'], field['label']}, id: {field_form_id}")

        if "options" in field and field["type"] != "datalist":
            if field["type"] == "switch":
                f_value = field["options"][1]["name"]
            else:
                selected_opts = [opt for opt in field["options"] if str(opt["id"]) == form_dict[field_form_id]]
                f_value = selected_opts[0]["name"] if len(selected_opts) > 0 else "N/A"
        else:
            f_value = form_dict[field_form_id]

        return f_name, convert_value(f_value,
                                     field["type"],
                                     field["dtype"])

    out_dict = {}

    for block, block_fields in field_mapping.items():
        for field in block_fields:

            field_form_id = f"{block[0]}^"  # ^{field['id']}"
            if field["type"] in ["vstack"]:
                field_form_id += "*1*"
            field_form_id += f"{field['id']}"

            if field["type"] in ["vstack"] and False:
                raise Exception(f"{field}")
                counter = 1
                while field_form_id.replace("NUM", str(counter)) in form_dict:
                    parse_res = parse_form_field(field_form_id.replace("NUM", str(counter)), field)
                    if parse_res[0] is None:
                        counter += 1
                        continue
                    parse_res[0] = parse_res[0] + f" {counter}"
                    out_dict[parse_res[0]] = parse_res[1]
                    counter += 1
            else:
                parse_res = parse_form_field(field_form_id, field)
                if parse_res[0] is None:
                    continue
                out_dict[parse_res[0]] = parse_res[1]

    for f_name in ["Масса тела", "Рост"]:
        unit_field_name = "единицы измерения " + str_to_genitive(f_name).lower()
        f_value = Value(out_dict[f_name], out_dict[unit_field_name])
        out_dict[f_name] = f_value

    out_dict = _unpack_analysis_items(out_dict)

    out_dict["only_en"] = form_dict["only_en"]
    out_dict["only_pen"] = form_dict["only_pen"]

    return out_dict


# def form_to_dict(form_dict, field_mapping):
#     def convert_value(val, _type=None, _dtype=None):
#         if val == "N/A":
#             return val
#         if val in ["да", "нет"]:
#             return val == "да"
#         if str_is_unit(val):
#             return val
#
#         assert _type is not None
#
#         if _type in ["select", "radio"]:
#             return val
#         elif _type == "datalist":
#             return val
#         elif _type == "input":
#             assert _dtype is not None
#
#             if _dtype == "number":
#                 return float(val) if len(val) > 0 else None
#             elif _dtype == "date":
#                 return date(*[int(pt) for pt in val.split("-")]) if len(val) > 0 else None
#             return val
#         else:
#             raise ValueError(f"Wrong field type provided: {[val, _type, _dtype]}!")
#
#     def str_to_genitive(s):
#         pts = s.split()
#         if pts[0][-1] == "а":
#             pts[0] = pts[0][:-1] + "ы"
#         elif pts[0][-1] == "т":
#             pts[0] = pts[0] + "а"
#         return " ".join(pts)
#
#     def parse_form_field(field_form_id, field):
#         # TODO: format conversion
#         f_name = field["label"]
#         if field_form_id not in list(form_dict.keys()):
#             if field["type"] == "radio":
#                 raise ValueError("All Radio buttons must be chosen!")
#             elif field["type"] == "switch":
#                 return f_name, convert_value(field["options"][0]["name"])
#             elif field["type"] in ["vstack", "hstack"]:
#                 if f_name in ["Смеси ЭП", "Растворы ПЭП"] and field_form_id[0] == '6':
#                     f_name = "Тек*" + f_name
#                 if field["type"] == "vstack" and ("Смеси ЭП" in f_name or "Растворы ПЭП" in f_name):
#                     cnt = 1
#                     res = {}
#                     child_id = field_form_id + "_" + str(field["options"][0]["id"])
#
#                     while len([1 for k in form_dict if child_id.replace("*1*", f"*{cnt}*") in k]) > 0:
#                         loc_res = parse_form_field(child_id.replace("*1*", f"*{cnt}*"), field["options"][0])
#                         res[loc_res[0] + f" {cnt}"] = loc_res[1]
#                         cnt += 1
#                     return f_name, res
#
#                 res = f_name, {parse_form_field(field_form_id + "_" + str(child["id"]), child)[0]:
#                                    parse_form_field(field_form_id + "_" + str(child["id"]), child)[1]
#                                for child in field["options"]}
#                 return res
#             elif field["type"] == "button":
#                 return None, None
#             else:
#                 raise Exception(f"How can it be?? {field['type'], field['label']}")
#
#         if "options" in field and field["type"] != "datalist":
#             if field["type"] == "switch":
#                 f_value = field["options"][1]["name"]
#             else:
#                 selected_opts = [opt for opt in field["options"] if str(opt["id"]) == form_dict[field_form_id]]
#                 f_value = selected_opts[0]["name"] if len(selected_opts) > 0 else "N/A"
#         else:
#             f_value = form_dict[field_form_id]
#
#         return f_name, convert_value(f_value,
#                                      field["type"],
#                                      field["dtype"])
#
#     out_dict = {}
#
#     for block, block_fields in field_mapping.items():
#         for field in block_fields:
#             field_form_id = f"{block[0]}^"  # ^{field['id']}"
#             if field["type"] in ["vstack"]:
#                 field_form_id += "*1*"
#             field_form_id += f"{field['id']}"
#
#             parse_res = parse_form_field(field_form_id, field)
#             if parse_res[0] is None:
#                 continue
#             out_dict[parse_res[0]] = parse_res[1]
#
#     for f_name in ["Масса тела", "Рост"]:
#         unit_field_name = "единицы измерения " + str_to_genitive(f_name).lower()
#         f_value = Value(out_dict[f_name], out_dict[unit_field_name])
#         out_dict[f_name] = f_value
#
#     return out_dict
