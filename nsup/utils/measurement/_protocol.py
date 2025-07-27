
class MeasurementUtilProtocol:
    _required_keys = None

    @classmethod
    def compute(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def _assert_keys(cls, keys):
        for key in cls._required_keys:
            if key not in keys:
                raise ValueError(f"{key} key must be provided!")
        return True
