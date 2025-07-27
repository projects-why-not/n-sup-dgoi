from ._protocol import PatientInfoProtocol


class Body(PatientInfoProtocol):
    _tgt_keys = ["Возраст", "Пол", "Вес", "Рост", "ИМТ"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
