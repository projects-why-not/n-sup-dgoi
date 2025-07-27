from dateutil.relativedelta import relativedelta
from datetime import date


class Age:
    def __init__(self, *args):
        """
        :param args:
        """
        assert 1 <= len(args) <= 3

        self.total_days = None

        if type(args[0]) is dict:
            self.years, self.months, self.days = args[0].get("лет", 0), args[0].get("мес", 0), args[0].get("дней", 0)
            if "нед" in args[0]:
                self.days += 7 * args[0]["нед"]
        elif len(args) == 2 and type(args[0]) is date and type(args[1]) is date:
            dt = relativedelta(args[0], args[1])
            self.years, self.months, self.days = dt.years, dt.months, dt.days
            self.total_days = (args[0] - args[1]).days
        elif len(set([type(a) for a in args])) == 1 and type(args[0]) is int:
            self.years, self.months, self.days = list(args) + [None] * (3 - len(args))
        else:
            raise ValueError("Wrong datatype provided!")

    def __eq__(self, other):
        assert type(other) is Age
        return self.years == other.years and self.months == other.months and self.days == other.days

    def __gt__(self, other):
        assert type(other) is Age
        if self.years < other.years:
            return False
        if self.years > other.years:
            return True
        if self.months > other.months:
            return True
        if self.months < other.months:
            return False
        return self.days > other.days

    def __lt__(self, other):
        return other > self

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return self < other or self == other

    def __getitem__(self, item):
        assert item in ["дней", "д", "мес", "м", "лет", "год"]

        if item in ["лет", "год"]:
            return self.years
        elif item in ["мес", "м"]:
            return self.years * 12 + self.months
        elif item in ["дней", "д"]:
            return self.total_days
