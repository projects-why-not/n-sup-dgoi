from ._step_protocol import NutritionDerivationProtocol
from numpy import inf


class EnergyDerivation(NutritionDerivationProtocol):
    @classmethod
    def compute(cls, patient, **kwargs):
        energy_basic = cls.energy_basic_f(patient["Возраст"]["лет"],
                                          int(patient["Пол"] == "Мужской"),
                                          patient["Масса тела"]["кг"],
                                          patient["Рост"]["м"])
        energy_due = cls.energy_due_f(energy_basic,
                                      patient["Возраст"]["лет"],
                                      patient["Масса тела"]["кг"],
                                      patient["Лихорадка  течение последних 2-х дней"],
                                      patient["Активность пациента"] == "активен и мобилен",
                                      patient["Активность пациента"] == "активность ограничена",
                                      patient["Активность пациента"] == "тяжелое состояние - требует поддержки жизненных функций",
                                      True,
                                      patient["Тяжелая белково-энергетическая недостаточность"],
                                      patient["Умеренная белково-энергетическая недостаточность"],
                                      patient["Легкая белково-энергетическая недостаточность"])
        if "due_only" in kwargs:
            return energy_due

        energy = cls.energy_f(energy_due,
                              patient["Риск рефидинг-синдрома"])

        # FIXME: what about bounds?
        return energy, [0, inf], energy_due

    @classmethod
    def energy_basic_f(cls,
                       age: int,
                       sex: int,
                       weight: float,
                       height: float) -> float:

        """
        Количество ккал для обеспечения основного обмена для пациента в сутки (Schofield вес+рост)


        :param age: возраст - полных лет
        :param sex: пол, 1 = мужской
        :param weight: вес, кг
        :param height: рост, м
        :return: количество ккал для основного обмена пациента в сутки
        """

        age_female_to_coefs = {
            1: (16.25, 1023.2, -413.5),
            2: (16.97, 161.8, 371.2),
            3: (8.365, 465, 200)
        }
        age_male_to_coefs = {
            1: (0.167, 1517.4, -617.6),
            2: (19.6, 130.3, 414.9),
            3: (16.25, 137.2, 515.5)
        }
        if sex == 1:
            a = age_male_to_coefs
        else:
            a = age_female_to_coefs

        i = (age >= 0) + (age >= 3) + (age >= 10)
        # print(i, a)
        coef_f, coef_s, coef_t = a[i]

        return coef_f * weight + coef_s * height + coef_t

    @classmethod
    def energy_due_f(cls,
                     energy_basic: float,
                     age: int,
                     weight: float,
                     fever: int,
                     m: int,
                     s: int,
                     v: int,
                     acute: int,
                     sev_maln: int,
                     mod_maln: int,
                     mild_maln: int) -> float:

        """
        Количество ккал для обеспечения потребности в энергии для пациента в сутки


        :param energy_basic: энергия основного обмена
        :param age: возраст - полных лет
        :param weight: вес, кг
        :param fever: "Лихорадка  течение последних 2-х дней" == True
        :param m: пациент активен и мобилен (параметр - активность)
        :param s: пациент с ограниченной активностью (параметр - активность)
        :param v: пациент нуждается в поддержке жизненных функций (параметр - активность)
        :param acute: активное заболевание - для всех пациентов стационара дефолтно TRUE
        :param sev_maln: наличие тяжелой БЭН
        :param mod_maln: наличие умеренной БЭН
        :param mild_maln: наличие легкой БЭН
        :return: количество ккал для пациента в сутки
        """

        acute = 1
        k = 1 + (0.1 * fever) + (0.3 * m + 0.2 * s + 0.1 * v) + (0.1 * acute) + (
                0.1 * mild_maln + 0.2 * mod_maln + 0.3 * sev_maln)
        en_due = energy_basic * k + (20 * weight) * (age == 0)
        return en_due

    @classmethod
    def energy_f(cls,
                 energy_due: float,
                 refeeding: float) -> float:

        """
        Количество ккал для обеспечения потребности в энергии для пациента в сутки с учетом рефидинг-синдрома


        :param energy_due: количество ккал для обеспечения потребности в энергии для пациента в сутки
        :param refeeding: риск рефидинг-синдрома
        :return: количество ккал для пациента в сутки
        """
        return energy_due * 0.4 + energy_due * 0.6 * (1 - refeeding)
