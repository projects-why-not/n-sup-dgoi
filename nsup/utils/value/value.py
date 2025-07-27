from .conversion import UnitConverter


class Value:
    def __init__(self, value, val_units):
        self.value = value
        self.units = val_units

    def __add__(self, other):
        if other.__class__ is Value:
            other = UnitConverter.convert(other.value,
                                          other.units,
                                          self.units)
            return Value(self.value + other.value, self.units)
        return Value(self.value + other, self.units)

    def __neg__(self):
        return Value(-self.value, self.units)

    def __sub__(self, other):
        return self.__add__(-other)

    def __mul__(self, other):
        if other.__class__ is Value:
            # if other.units != self.units:
            #     other = UnitConverter.convert(other.value, other.units, self.units)
            return Value(self.value * other.value, f"{self.units}*{self.units}")
        return Value(self.value * other, self.units)

    def __truediv__(self, other):
        if other.__class__ is Value:
            # if other.units != self.units:
            #     other = UnitConverter.convert(other.value, other.units, self.units)
            return Value(self.value / other.value, f"{self.units}/{self.units}")
        return Value(self.value / other, self.units)

    def __getitem__(self, tgt_units):
        return Value(UnitConverter.convert(self.value, self.units, tgt_units),
                     tgt_units).value
