from ..utils.constants.db import *
from ..utils.db import DBProvider
from ..utils.form import form_to_json, form_to_dict
from ..utils.value import Value
from ..patient import PatientInfo
from ..nutrition import NutritionRecommender

from flask import Flask, render_template, redirect, url_for, request, send_file, jsonify
from os import sep, remove
from datetime import datetime, timedelta
import json


if __name__ == "__main__":
    db_provider = DBProvider(DB_NAME,
                             DB_USER,
                             DB_PASSWD)
    data_config = db_provider.get_data_config()
    self_path = sep.join(__file__.split(sep)[:-1]) + sep
    last_interface_update_time = datetime.now()

    webapp = Flask(__name__,
                   static_url_path='/nutrition/',
                   template_folder=self_path + "templates/",
                   static_folder=self_path + "static/")

    @webapp.route("/nutrition", methods=["GET"])
    def home():
        # data_config = db_provider.get_data_config()
        # return jsonify(data_config)
        """
        global last_interface_update_time

        if (datetime.now() - last_interface_update_time).total_seconds() / 60 >= 1:
            global data_config
            data_config = db_provider.get_data_config()
            last_interface_update_time = datetime.now()
        """
        return render_template("new_patient_clear.html", req_data=data_config)


    @webapp.route("/nutrition", methods=["POST"])
    def handle_post():
        form = request.form
        if "submit" in form.keys():
            patient = PatientInfo(form, db_provider)

            recommendations = NutritionRecommender(patient, db_provider).get_recommendations()
            recommendations = json.dumps(recommendations)

            return recommendations

        elif "get_json" in form.keys():
            # FIXME: make json, return as file
            out_path = form_to_json(form, data_config)
            return send_file(out_path)

        elif "add_to_db" in form.keys():
            # FIXME: add record to database
            pass
        else:
            return jsonify({"err": "unknown request"}), 200
else:
    webapp = None
