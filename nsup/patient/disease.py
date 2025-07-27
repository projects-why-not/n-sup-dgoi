from ._protocol import PatientInfoProtocol


class Therapy(PatientInfoProtocol):
    _tgt_keys = ["phase", "medicine"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class Disease(PatientInfoProtocol):
    _tgt_keys = ["diagnosis", "therapy"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
