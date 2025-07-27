

units = {
    "length": {"m": 1,
               "cm": 100,
               "dm": 10,
               "mm": 1000,
               "km": 0.001,

               "м": 1,
               "см": 100,
               "дм": 10,
               "мм": 1000,
               "км": 0.001,
               },
    "weight": {"kg": 1,
               "g": 1000,
               "mg": 1000000,

               "кг": 1,
               "г": 1000,
               "мг": 1000000
               }
}


def str_is_unit(s):
    for t, un_list in units.items():
        if s in un_list.keys():
            return True
    return False
