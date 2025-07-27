
class PatientInfoProtocol:
    _tgt_keys = None

    def __init__(self, **kwargs):
        self._values = {k: kwargs[k]
                        for k in self._tgt_keys}

    def get_keys(self):
        return self._tgt_keys

    def get_data(self):
        return self._values

    def __getitem__(self, item):
        assert item in self._values
        return self._values[item]
