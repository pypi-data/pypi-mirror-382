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

BJSubdivisionCodeType = Literal[
    "BJ-AK",  # Atacora
    "BJ-AL",  # Alibori
    "BJ-AQ",  # Atlantique
    "BJ-BO",  # Borgou
    "BJ-CO",  # Collines
    "BJ-DO",  # Donga
    "BJ-KO",  # Couffo
    "BJ-LI",  # Littoral
    "BJ-MO",  # Mono
    "BJ-OU",  # Ouémé
    "BJ-PL",  # Plateau
    "BJ-ZO",  # Zou
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BJSubdivision(Subdivision):
    code: BJSubdivisionCodeType


BJ: Final[Country] = Country(
    alpha2="BJ",
    alpha3="BEN",
    name="Benin",
    common_name=None,
    official_name="Republic of Benin",
    subdivisions=[
        BJSubdivision(code="BJ-AK", name="Atacora", type_="Department"),
        BJSubdivision(code="BJ-AL", name="Alibori", type_="Department"),
        BJSubdivision(code="BJ-AQ", name="Atlantique", type_="Department"),
        BJSubdivision(code="BJ-BO", name="Borgou", type_="Department"),
        BJSubdivision(code="BJ-CO", name="Collines", type_="Department"),
        BJSubdivision(code="BJ-DO", name="Donga", type_="Department"),
        BJSubdivision(code="BJ-KO", name="Couffo", type_="Department"),
        BJSubdivision(code="BJ-LI", name="Littoral", type_="Department"),
        BJSubdivision(code="BJ-MO", name="Mono", type_="Department"),
        BJSubdivision(code="BJ-OU", name="Ouémé", type_="Department"),
        BJSubdivision(code="BJ-PL", name="Plateau", type_="Department"),
        BJSubdivision(code="BJ-ZO", name="Zou", type_="Department"),
    ],
)
