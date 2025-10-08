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

LYSubdivisionCodeType = Literal[
    "LY-BA",  # Banghāzī
    "LY-BU",  # Al Buţnān
    "LY-DR",  # Darnah
    "LY-GT",  # Ghāt
    "LY-JA",  # Al Jabal al Akhḑar
    "LY-JG",  # Al Jabal al Gharbī
    "LY-JI",  # Al Jafārah
    "LY-JU",  # Al Jufrah
    "LY-KF",  # Al Kufrah
    "LY-MB",  # Al Marqab
    "LY-MI",  # Mişrātah
    "LY-MJ",  # Al Marj
    "LY-MQ",  # Murzuq
    "LY-NL",  # Nālūt
    "LY-NQ",  # An Nuqāţ al Khams
    "LY-SB",  # Sabhā
    "LY-SR",  # Surt
    "LY-TB",  # Ţarābulus
    "LY-WA",  # Al Wāḩāt
    "LY-WD",  # Wādī al Ḩayāt
    "LY-WS",  # Wādī ash Shāţi’
    "LY-ZA",  # Az Zāwiyah
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class LYSubdivision(Subdivision):
    code: LYSubdivisionCodeType


LY: Final[Country] = Country(
    alpha2="LY",
    alpha3="LBY",
    name="Libya",
    common_name=None,
    official_name="Libya",
    subdivisions=[
        LYSubdivision(code="LY-BA", name="Banghāzī", type_="Popularate"),
        LYSubdivision(code="LY-BU", name="Al Buţnān", type_="Popularate"),
        LYSubdivision(code="LY-DR", name="Darnah", type_="Popularate"),
        LYSubdivision(code="LY-GT", name="Ghāt", type_="Popularate"),
        LYSubdivision(code="LY-JA", name="Al Jabal al Akhḑar", type_="Popularate"),
        LYSubdivision(code="LY-JG", name="Al Jabal al Gharbī", type_="Popularate"),
        LYSubdivision(code="LY-JI", name="Al Jafārah", type_="Popularate"),
        LYSubdivision(code="LY-JU", name="Al Jufrah", type_="Popularate"),
        LYSubdivision(code="LY-KF", name="Al Kufrah", type_="Popularate"),
        LYSubdivision(code="LY-MB", name="Al Marqab", type_="Popularate"),
        LYSubdivision(code="LY-MI", name="Mişrātah", type_="Popularate"),
        LYSubdivision(code="LY-MJ", name="Al Marj", type_="Popularate"),
        LYSubdivision(code="LY-MQ", name="Murzuq", type_="Popularate"),
        LYSubdivision(code="LY-NL", name="Nālūt", type_="Popularate"),
        LYSubdivision(code="LY-NQ", name="An Nuqāţ al Khams", type_="Popularate"),
        LYSubdivision(code="LY-SB", name="Sabhā", type_="Popularate"),
        LYSubdivision(code="LY-SR", name="Surt", type_="Popularate"),
        LYSubdivision(code="LY-TB", name="Ţarābulus", type_="Popularate"),
        LYSubdivision(code="LY-WA", name="Al Wāḩāt", type_="Popularate"),
        LYSubdivision(code="LY-WD", name="Wādī al Ḩayāt", type_="Popularate"),
        LYSubdivision(code="LY-WS", name="Wādī ash Shāţi’", type_="Popularate"),
        LYSubdivision(code="LY-ZA", name="Az Zāwiyah", type_="Popularate"),
    ],
)
