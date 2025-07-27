from mysql.connector import connect, Error


class DBWrapper:
    def __init__(self, db_name, db_login, db_passwd, db_host, db_port):
        self.cursor = None
        self.db_host = db_host
        self.db_login = db_login
        self.db_passwd = db_passwd
        self.db_name = db_name
        self.db_port = db_port
        self.connection = None
        # self.connect()

    def connect(self):
        try:
            self.connection = connect(
                host=self.db_host,
                user=self.db_login,
                password=self.db_passwd,
                database=self.db_name,
                port=self.db_port)
            self.cursor = self.connection.cursor()
        except Error as e:
            print(e)
            return False
        return True

    def disconnect(self):
        self.cursor.close()
        self.connection.close()

    def _select(self, query):
        self.connect()
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
        except:
            self.disconnect()
            raise Exception(query)

        self.disconnect()
        return results

    def _select_m(self, table, sel_keys, and_conditions=None):
        query = f"SELECT {','.join(sel_keys)} FROM {table}"
        if and_conditions is not None:
            query += " WHERE "
            for k, cond in enumerate(and_conditions):
                query += " ".join(cond)
                if k < len(and_conditions) - 1:
                    query += " AND "
        query += ";"

        return self._select(query)

    def _insert(self, table, keys, values):
        query = f"INSERT INTO {table} ({', '.join(keys)}) VALUES (" + ("%s, " * (len(keys) - 1)) + "%s)"
        self.connect()
        try:
            # for val_set in values:
            if type(values[0]) not in [tuple, list]:
                self.cursor.execute(query, values)
            else:
                self.cursor.executemany(query, values)

            self.connection.commit()
        except Exception as e:
            self.disconnect()

            raise Exception(f"{str(e)}\n{query}\n{keys} / {values}")

            return False

        self.disconnect()
        return True

    def get_blocks(self):
        return self._select("SELECT id, name FROM in_status_block ORDER BY number;")

    def get_subblock_fields(self, subblock_id):
        return self._select(f"SELECT in_data_item.id, in_data_item.label, in_data_type.tag, in_input_type.type, in_data_item.units, in_input_type.onChangeMethod, in_data_item.onChange, in_data_item.defaultValue, in_data_item.is_required, in_data_item.attributes FROM (in_item_block_grouping LEFT JOIN in_data_item ON in_item_block_grouping.subitem_id = in_data_item.id LEFT JOIN in_input_type ON in_data_item.dtype_id = in_input_type.id LEFT JOIN in_data_type ON in_data_item.type_id = in_data_type.id) WHERE in_item_block_grouping.block_item_id = {subblock_id} ORDER BY in_item_block_grouping.number;")

    def get_block_fields(self, block_id):
        return self._select(f"SELECT in_data_item.id, in_data_item.label, in_data_type.tag, in_input_type.type, in_data_item.units, in_input_type.onChangeMethod, in_data_item.onChange, in_data_item.defaultValue, in_data_item.is_required, in_data_item.attributes FROM "
                            f"(in_block_item_order LEFT JOIN in_data_item ON in_block_item_order.data_item_id = in_data_item.id "
                            f"LEFT JOIN in_input_type ON in_data_item.dtype_id = in_input_type.id "
                            f"LEFT JOIN in_data_type ON in_data_item.type_id = in_data_type.id) "
                            f"WHERE in_block_item_order.block_id = {block_id} ORDER BY in_block_item_order.number;")

    def get_selection_options(self, sel_id, item_label):
        return self._select(f"SELECT in_data_option.id, in_data_option.name FROM in_options "
                            f"LEFT JOIN in_data_item ON in_options.item_id = in_data_item.id "
                            f"LEFT JOIN in_data_option ON in_options.opt_id = in_data_option.id "
                            f"WHERE in_data_item.id = {sel_id};")

    def get_nutrition(self, enternal, only_available=False):
        return self._select(f"SELECT id, name FROM nutrition WHERE " + ("is_available = 1 AND" if only_available else "") + f" is_enteral = {int(enternal)} ORDER BY name;")

    def get_nutrition_key_features(self, enteral):
        query = f"SELECT nutrition.name, nutrition_feature.name, nutrition_feature_value.value FROM nutrition_feature_value LEFT JOIN nutrition ON nutrient_id = nutrition.id LEFT JOIN nutrition_feature ON feature_id = nutrition_feature.id WHERE nutrition.is_enteral = {int(enteral)};"
        return self._select(query)

    def get_clinical_limits(self, analysis_name, sex):
        sex = int(sex == "M")  #  if sex == "М" else "F"
        return self._select(f"SELECT * FROM clinical_limits WHERE name = '{analysis_name}' AND male = '{sex}'")

    def get_all_clinical_limits(self, sex):
        analyses = self._select("SELECT DISTINCT name FROM clinical_limits ORDER BY name;")
        res = {}
        for row in analyses:
            res[row[0]] = self.get_clinical_limits(row[0], sex)
        return res

    def get_derived_parameters(self):
        return self._select("SELECT id, name, calc_function FROM derived_parameter ORDER BY computation_order;")

    def get_derived_params_reference(self):
        return self._select(f"SELECT der_param_id, label, derived_parameter.name FROM derived_parameter_reference LEFT JOIN in_data_item ON derived_parameter_reference.ref_data_item_id = in_data_item.id LEFT JOIN derived_parameter ON derived_parameter_reference.ref_der_param_id = derived_parameter.id;")

    def get_derived_params_appendices(self):
        return self._select("SELECT * FROM derived_parameter_appendix;")

    def get_nutrition_tags(self, enteral=None):
        filter_condition = ""
        if enteral in [True, False]:
            filter_condition = f"WHERE is_enteral = {int(enteral)}"
        return self._select(f"SELECT nutrition.name, nutrition_tag.tag FROM nutrition_tagging LEFT JOIN nutrition ON nutrient_id = nutrition.id LEFT JOIN nutrition_tag ON tag_id = nutrition_tag.id {filter_condition} ORDER BY nutrition.name")
