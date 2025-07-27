from ._protocol import PatientInfoProtocol


class BloodInfo(PatientInfoProtocol):
    _tgt_keys = []  # FIXME: add keys

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ClinicalStatus(PatientInfoProtocol):
    _tgt_keys = []  # FIXME: add keys

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class NutritionalStatus(PatientInfoProtocol):
    _tgt_keys = []  # FIXME: add keys

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
