# SPDX-FileCopyrightText: 2024-present Trenton H <rda0128ou@mozmail.com>
#
# SPDX-License-Identifier: MPL-2.0
# Generated from:
#  Country Data: d055275324963c9bce5882eaaa93024cf2bf7ed0
#  Subdivision Data: 4f5658fa63afce8cd121d41444b28c2294e6b513
import dataclasses
from typing import Final
from typing import Literal

from simpleiso3166.base import DATACLASS_BASE_AGS
from simpleiso3166.base import Country
from simpleiso3166.base import Subdivision

LTSubdivisionCodeType = Literal[
    "LT-01",  # Akmenė
    "LT-02",  # Alytaus miestas
    "LT-03",  # Alytus
    "LT-04",  # Anykščiai
    "LT-05",  # Birštonas
    "LT-06",  # Biržai
    "LT-07",  # Druskininkai
    "LT-08",  # Elektrėnai
    "LT-09",  # Ignalina
    "LT-10",  # Jonava
    "LT-11",  # Joniškis
    "LT-12",  # Jurbarkas
    "LT-13",  # Kaišiadorys
    "LT-14",  # Kalvarija
    "LT-15",  # Kauno miestas
    "LT-16",  # Kaunas
    "LT-17",  # Kazlų Rūdos
    "LT-18",  # Kėdainiai
    "LT-19",  # Kelmė
    "LT-20",  # Klaipėdos miestas
    "LT-21",  # Klaipėda
    "LT-22",  # Kretinga
    "LT-23",  # Kupiškis
    "LT-24",  # Lazdijai
    "LT-25",  # Marijampolė
    "LT-26",  # Mažeikiai
    "LT-27",  # Molėtai
    "LT-28",  # Neringa
    "LT-29",  # Pagėgiai
    "LT-30",  # Pakruojis
    "LT-31",  # Palangos miestas
    "LT-32",  # Panevėžio miestas
    "LT-33",  # Panevėžys
    "LT-34",  # Pasvalys
    "LT-35",  # Plungė
    "LT-36",  # Prienai
    "LT-37",  # Radviliškis
    "LT-38",  # Raseiniai
    "LT-39",  # Rietavas
    "LT-40",  # Rokiškis
    "LT-41",  # Šakiai
    "LT-42",  # Šalčininkai
    "LT-43",  # Šiaulių miestas
    "LT-44",  # Šiauliai
    "LT-45",  # Šilalė
    "LT-46",  # Šilutė
    "LT-47",  # Širvintos
    "LT-48",  # Skuodas
    "LT-49",  # Švenčionys
    "LT-50",  # Tauragė
    "LT-51",  # Telšiai
    "LT-52",  # Trakai
    "LT-53",  # Ukmergė
    "LT-54",  # Utena
    "LT-55",  # Varėna
    "LT-56",  # Vilkaviškis
    "LT-57",  # Vilniaus miestas
    "LT-58",  # Vilnius
    "LT-59",  # Visaginas
    "LT-60",  # Zarasai
    "LT-AL",  # Alytaus apskritis
    "LT-KL",  # Klaipėdos apskritis
    "LT-KU",  # Kauno apskritis
    "LT-MR",  # Marijampolės apskritis
    "LT-PN",  # Panevėžio apskritis
    "LT-SA",  # Šiaulių apskritis
    "LT-TA",  # Tauragės apskritis
    "LT-TE",  # Telšių apskritis
    "LT-UT",  # Utenos apskritis
    "LT-VL",  # Vilniaus apskritis
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class LTSubdivision(Subdivision):
    code: LTSubdivisionCodeType


LT: Final[Country] = Country(
    alpha2="LT",
    alpha3="LTU",
    name="Lithuania",
    common_name=None,
    official_name="Republic of Lithuania",
    subdivisions=[
        LTSubdivision(code="LT-01", name="Akmenė", type_="District municipality"),
        LTSubdivision(code="LT-02", name="Alytaus miestas", type_="City municipality"),
        LTSubdivision(code="LT-03", name="Alytus", type_="District municipality"),
        LTSubdivision(code="LT-04", name="Anykščiai", type_="District municipality"),
        LTSubdivision(code="LT-05", name="Birštonas", type_="Municipality"),
        LTSubdivision(code="LT-06", name="Biržai", type_="District municipality"),
        LTSubdivision(code="LT-07", name="Druskininkai", type_="Municipality"),
        LTSubdivision(code="LT-08", name="Elektrėnai", type_="Municipality"),
        LTSubdivision(code="LT-09", name="Ignalina", type_="District municipality"),
        LTSubdivision(code="LT-10", name="Jonava", type_="District municipality"),
        LTSubdivision(code="LT-11", name="Joniškis", type_="District municipality"),
        LTSubdivision(code="LT-12", name="Jurbarkas", type_="District municipality"),
        LTSubdivision(code="LT-13", name="Kaišiadorys", type_="District municipality"),
        LTSubdivision(code="LT-14", name="Kalvarija", type_="Municipality"),
        LTSubdivision(code="LT-15", name="Kauno miestas", type_="City municipality"),
        LTSubdivision(code="LT-16", name="Kaunas", type_="District municipality"),
        LTSubdivision(code="LT-17", name="Kazlų Rūdos", type_="Municipality"),
        LTSubdivision(code="LT-18", name="Kėdainiai", type_="District municipality"),
        LTSubdivision(code="LT-19", name="Kelmė", type_="District municipality"),
        LTSubdivision(code="LT-20", name="Klaipėdos miestas", type_="City municipality"),
        LTSubdivision(code="LT-21", name="Klaipėda", type_="District municipality"),
        LTSubdivision(code="LT-22", name="Kretinga", type_="District municipality"),
        LTSubdivision(code="LT-23", name="Kupiškis", type_="District municipality"),
        LTSubdivision(code="LT-24", name="Lazdijai", type_="District municipality"),
        LTSubdivision(code="LT-25", name="Marijampolė", type_="District municipality"),
        LTSubdivision(code="LT-26", name="Mažeikiai", type_="District municipality"),
        LTSubdivision(code="LT-27", name="Molėtai", type_="District municipality"),
        LTSubdivision(code="LT-28", name="Neringa", type_="Municipality"),
        LTSubdivision(code="LT-29", name="Pagėgiai", type_="Municipality"),
        LTSubdivision(code="LT-30", name="Pakruojis", type_="District municipality"),
        LTSubdivision(code="LT-31", name="Palangos miestas", type_="City municipality"),
        LTSubdivision(code="LT-32", name="Panevėžio miestas", type_="City municipality"),
        LTSubdivision(code="LT-33", name="Panevėžys", type_="District municipality"),
        LTSubdivision(code="LT-34", name="Pasvalys", type_="District municipality"),
        LTSubdivision(code="LT-35", name="Plungė", type_="District municipality"),
        LTSubdivision(code="LT-36", name="Prienai", type_="District municipality"),
        LTSubdivision(code="LT-37", name="Radviliškis", type_="District municipality"),
        LTSubdivision(code="LT-38", name="Raseiniai", type_="District municipality"),
        LTSubdivision(code="LT-39", name="Rietavas", type_="Municipality"),
        LTSubdivision(code="LT-40", name="Rokiškis", type_="District municipality"),
        LTSubdivision(code="LT-41", name="Šakiai", type_="District municipality"),
        LTSubdivision(code="LT-42", name="Šalčininkai", type_="District municipality"),
        LTSubdivision(code="LT-43", name="Šiaulių miestas", type_="City municipality"),
        LTSubdivision(code="LT-44", name="Šiauliai", type_="District municipality"),
        LTSubdivision(code="LT-45", name="Šilalė", type_="District municipality"),
        LTSubdivision(code="LT-46", name="Šilutė", type_="District municipality"),
        LTSubdivision(code="LT-47", name="Širvintos", type_="District municipality"),
        LTSubdivision(code="LT-48", name="Skuodas", type_="District municipality"),
        LTSubdivision(code="LT-49", name="Švenčionys", type_="District municipality"),
        LTSubdivision(code="LT-50", name="Tauragė", type_="District municipality"),
        LTSubdivision(code="LT-51", name="Telšiai", type_="District municipality"),
        LTSubdivision(code="LT-52", name="Trakai", type_="District municipality"),
        LTSubdivision(code="LT-53", name="Ukmergė", type_="District municipality"),
        LTSubdivision(code="LT-54", name="Utena", type_="District municipality"),
        LTSubdivision(code="LT-55", name="Varėna", type_="District municipality"),
        LTSubdivision(code="LT-56", name="Vilkaviškis", type_="District municipality"),
        LTSubdivision(code="LT-57", name="Vilniaus miestas", type_="City municipality"),
        LTSubdivision(code="LT-58", name="Vilnius", type_="District municipality"),
        LTSubdivision(code="LT-59", name="Visaginas", type_="Municipality"),
        LTSubdivision(code="LT-60", name="Zarasai", type_="District municipality"),
        LTSubdivision(code="LT-AL", name="Alytaus apskritis", type_="County"),
        LTSubdivision(code="LT-KL", name="Klaipėdos apskritis", type_="County"),
        LTSubdivision(code="LT-KU", name="Kauno apskritis", type_="County"),
        LTSubdivision(code="LT-MR", name="Marijampolės apskritis", type_="County"),
        LTSubdivision(code="LT-PN", name="Panevėžio apskritis", type_="County"),
        LTSubdivision(code="LT-SA", name="Šiaulių apskritis", type_="County"),
        LTSubdivision(code="LT-TA", name="Tauragės apskritis", type_="County"),
        LTSubdivision(code="LT-TE", name="Telšių apskritis", type_="County"),
        LTSubdivision(code="LT-UT", name="Utenos apskritis", type_="County"),
        LTSubdivision(code="LT-VL", name="Vilniaus apskritis", type_="County"),
    ],
)
