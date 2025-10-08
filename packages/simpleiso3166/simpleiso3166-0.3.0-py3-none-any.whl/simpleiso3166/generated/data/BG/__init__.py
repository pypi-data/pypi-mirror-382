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

BGSubdivisionCodeType = Literal[
    "BG-01",  # Blagoevgrad
    "BG-02",  # Burgas
    "BG-03",  # Varna
    "BG-04",  # Veliko Tarnovo
    "BG-05",  # Vidin
    "BG-06",  # Vratsa
    "BG-07",  # Gabrovo
    "BG-08",  # Dobrich
    "BG-09",  # Kardzhali
    "BG-10",  # Kyustendil
    "BG-11",  # Lovech
    "BG-12",  # Montana
    "BG-13",  # Pazardzhik
    "BG-14",  # Pernik
    "BG-15",  # Pleven
    "BG-16",  # Plovdiv
    "BG-17",  # Razgrad
    "BG-18",  # Ruse
    "BG-19",  # Silistra
    "BG-20",  # Sliven
    "BG-21",  # Smolyan
    "BG-22",  # Sofia (stolitsa)
    "BG-23",  # Sofia
    "BG-24",  # Stara Zagora
    "BG-25",  # Targovishte
    "BG-26",  # Haskovo
    "BG-27",  # Shumen
    "BG-28",  # Yambol
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BGSubdivision(Subdivision):
    code: BGSubdivisionCodeType


BG: Final[Country] = Country(
    alpha2="BG",
    alpha3="BGR",
    name="Bulgaria",
    common_name=None,
    official_name="Republic of Bulgaria",
    subdivisions=[
        BGSubdivision(code="BG-01", name="Blagoevgrad", type_="District"),
        BGSubdivision(code="BG-02", name="Burgas", type_="District"),
        BGSubdivision(code="BG-03", name="Varna", type_="District"),
        BGSubdivision(code="BG-04", name="Veliko Tarnovo", type_="District"),
        BGSubdivision(code="BG-05", name="Vidin", type_="District"),
        BGSubdivision(code="BG-06", name="Vratsa", type_="District"),
        BGSubdivision(code="BG-07", name="Gabrovo", type_="District"),
        BGSubdivision(code="BG-08", name="Dobrich", type_="District"),
        BGSubdivision(code="BG-09", name="Kardzhali", type_="District"),
        BGSubdivision(code="BG-10", name="Kyustendil", type_="District"),
        BGSubdivision(code="BG-11", name="Lovech", type_="District"),
        BGSubdivision(code="BG-12", name="Montana", type_="District"),
        BGSubdivision(code="BG-13", name="Pazardzhik", type_="District"),
        BGSubdivision(code="BG-14", name="Pernik", type_="District"),
        BGSubdivision(code="BG-15", name="Pleven", type_="District"),
        BGSubdivision(code="BG-16", name="Plovdiv", type_="District"),
        BGSubdivision(code="BG-17", name="Razgrad", type_="District"),
        BGSubdivision(code="BG-18", name="Ruse", type_="District"),
        BGSubdivision(code="BG-19", name="Silistra", type_="District"),
        BGSubdivision(code="BG-20", name="Sliven", type_="District"),
        BGSubdivision(code="BG-21", name="Smolyan", type_="District"),
        BGSubdivision(code="BG-22", name="Sofia (stolitsa)", type_="District"),
        BGSubdivision(code="BG-23", name="Sofia", type_="District"),
        BGSubdivision(code="BG-24", name="Stara Zagora", type_="District"),
        BGSubdivision(code="BG-25", name="Targovishte", type_="District"),
        BGSubdivision(code="BG-26", name="Haskovo", type_="District"),
        BGSubdivision(code="BG-27", name="Shumen", type_="District"),
        BGSubdivision(code="BG-28", name="Yambol", type_="District"),
    ],
)
