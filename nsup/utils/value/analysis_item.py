
class Analysis(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        assert "Дата анализа" in self.keys()
        assert len(self) == 2

        self._an_key = [key for key in self.keys() if key != "Дата анализа"][0]

        # TODO: default value?
        if self[self._an_key] is None:
            self[self._an_key] = -1

    def __add__(self, other):
        return self[self._an_key] + other

    def __mul__(self, other):
        return self[self._an_key] * other

    def __truediv__(self, other):
        return self[self._an_key] / other

    def __eq__(self, other):
        return self[self._an_key] == other

    def __gt__(self, other):
        return self[self._an_key] > other

    def __lt__(self, other):
        return self[self._an_key] < other

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return self < other or self == other
