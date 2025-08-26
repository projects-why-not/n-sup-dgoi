from ..utils.constants.db import *
from ..utils.db import DBProvider
from ..utils.form import form_to_json, form_to_dict, file_to_dict
from ..utils.value import Value
from ..patient import PatientInfo
from ..nutrition import NutritionRecommender

from flask import Flask, render_template, redirect, url_for, request, send_file, jsonify
from os import sep, remove
from datetime import datetime, timedelta
import traceback
import json


# if __name__ == "__main__":

db_provider = DBProvider(DB_NAME,
                         DB_USER,
                         DB_PASSWD, DB_HOST, DB_PORT)
data_config = db_provider.get_data_config()
self_path = sep.join(__file__.split(sep)[:-1]) + sep
last_interface_update_time = datetime.now()

webapp = Flask(__name__,
               static_url_path='/nutrition/',
               template_folder=self_path + "templates/",
               static_folder=self_path + "static/")


# @webapp.route("/nutrition/", defaults={"nutr_type": "all"}, methods=["GET"])
@webapp.route("/nutrition/pen_en", methods=["GET"])
def home():
    data_config = db_provider.get_data_config()
    return render_template("new_patient_clear.html", req_data=data_config, admin=False)


@webapp.route("/nutrition/en", methods=["GET"])
def home_en():
    data_config = db_provider.get_data_config(only_en=True)
    return render_template("new_patient_clear.html", req_data=data_config, admin=False, only_en=True)


@webapp.route("/nutrition", methods=["POST"])
def handle_post():
    form = request.form

    print(form, "\n\n", len(form))

    try:
        if len(form) == 1 or "submit" in form.keys():
            # return "ERR: currently unavailable"

            if len(form) == 1:
                local_form = file_to_dict(list(form.keys())[0])
            else:
                local_form = form_to_dict(form, data_config)

            print(local_form)

            patient_info = PatientInfo(local_form, db_provider)
            dict_out_template = "<html><head><meta charset='utf-8'></head><body>{}</body></html>"
            recommender = NutritionRecommender(patient_info, db_provider)
            recommendations = recommender.get_recommendations()

            # recommendations = [rec_set.get_recommendations() for rec_set in recommendations]

            # lp1 = recommendations[0]["LP сипинг"].variablesDict()
            # lp1 = {k: v.value() for k,v in lp1.items()}
            # lp2 = recommendations[0]["LP зонд"].variablesDict()
            # return f"{lp1}\n\n\n"

            # for i in range(len(recommendations)):
            #     recommendations[i]["id"] = i + 1

            # return f"ERR: {recommendations}"
            # return render_template("recommendations.html", recommendations=recommendations)
            return f"{recommendations}"

        elif "get_json" in form.keys():
            return "ERR: currently unavailable"
            # FIXME: make json, return as file
            out_path = form_to_json(form, data_config)
            return send_file(out_path)
        elif "add_to_db" in form.keys():
            # return f"ERR: {form}"

            f = open(f"/tmp/{form.get('1^7', 'test')}-{time()}.json", "w")
            f.write(f"{form}")
            f.close()
            return "MSG: OK"
        else:
            return jsonify({"err": "unknown request"}), 200
    except Exception as e:
        return f"ERR: {traceback.format_exc()}"

#
# @webapp.route("/nutrition", methods=["GET"])
# def home():
#     # data_config = db_provider.get_data_config()
#     # return jsonify(data_config)
#     """
#     global last_interface_update_time
#
#     if (datetime.now() - last_interface_update_time).total_seconds() / 60 >= 1:
#         global data_config
#         data_config = db_provider.get_data_config()
#         last_interface_update_time = datetime.now()
#     """
#     return render_template("new_patient_clear.html", req_data=data_config)


# @webapp.route("/nutrition", methods=["POST"])
# def handle_post():
#     form = request.form
#     if "submit" in form.keys():
#         patient = PatientInfo(form, db_provider)
#
#         recommendations = NutritionRecommender(patient, db_provider).get_recommendations()
#         recommendations = json.dumps(recommendations)
#
#         return recommendations
#
#     elif "get_json" in form.keys():
#         # FIXME: make json, return as file
#         out_path = form_to_json(form, data_config)
#         return send_file(out_path)
#
#     elif "add_to_db" in form.keys():
#         # FIXME: add record to database
#         pass
#     else:
#         return jsonify({"err": "unknown request"}), 200


# else:
#     webapp = None
