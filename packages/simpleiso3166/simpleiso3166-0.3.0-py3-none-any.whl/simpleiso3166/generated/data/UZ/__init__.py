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

UZSubdivisionCodeType = Literal[
    "UZ-AN",  # Andijon
    "UZ-BU",  # Buxoro
    "UZ-FA",  # Farg‘ona
    "UZ-JI",  # Jizzax
    "UZ-NG",  # Namangan
    "UZ-NW",  # Navoiy
    "UZ-QA",  # Qashqadaryo
    "UZ-QR",  # Qoraqalpog‘iston Respublikasi
    "UZ-SA",  # Samarqand
    "UZ-SI",  # Sirdaryo
    "UZ-SU",  # Surxondaryo
    "UZ-TK",  # Toshkent
    "UZ-TO",  # Toshkent
    "UZ-XO",  # Xorazm
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class UZSubdivision(Subdivision):
    code: UZSubdivisionCodeType


UZ: Final[Country] = Country(
    alpha2="UZ",
    alpha3="UZB",
    name="Uzbekistan",
    common_name=None,
    official_name="Republic of Uzbekistan",
    subdivisions=[
        UZSubdivision(code="UZ-AN", name="Andijon", type_="Region"),
        UZSubdivision(code="UZ-BU", name="Buxoro", type_="Region"),
        UZSubdivision(code="UZ-FA", name="Farg‘ona", type_="Region"),
        UZSubdivision(code="UZ-JI", name="Jizzax", type_="Region"),
        UZSubdivision(code="UZ-NG", name="Namangan", type_="Region"),
        UZSubdivision(code="UZ-NW", name="Navoiy", type_="Region"),
        UZSubdivision(code="UZ-QA", name="Qashqadaryo", type_="Region"),
        UZSubdivision(code="UZ-QR", name="Qoraqalpog‘iston Respublikasi", type_="Republic"),
        UZSubdivision(code="UZ-SA", name="Samarqand", type_="Region"),
        UZSubdivision(code="UZ-SI", name="Sirdaryo", type_="Region"),
        UZSubdivision(code="UZ-SU", name="Surxondaryo", type_="Region"),
        UZSubdivision(code="UZ-TK", name="Toshkent", type_="City"),
        UZSubdivision(code="UZ-TO", name="Toshkent", type_="Region"),
        UZSubdivision(code="UZ-XO", name="Xorazm", type_="Region"),
    ],
)
