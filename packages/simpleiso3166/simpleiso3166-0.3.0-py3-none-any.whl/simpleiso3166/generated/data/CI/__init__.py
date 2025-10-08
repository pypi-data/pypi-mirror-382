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

CISubdivisionCodeType = Literal[
    "CI-AB",  # Abidjan
    "CI-BS",  # Bas-Sassandra
    "CI-CM",  # Comoé
    "CI-DN",  # Denguélé
    "CI-GD",  # Gôh-Djiboua
    "CI-LC",  # Lacs
    "CI-LG",  # Lagunes
    "CI-MG",  # Montagnes
    "CI-SM",  # Sassandra-Marahoué
    "CI-SV",  # Savanes
    "CI-VB",  # Vallée du Bandama
    "CI-WR",  # Woroba
    "CI-YM",  # Yamoussoukro
    "CI-ZZ",  # Zanzan
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class CISubdivision(Subdivision):
    code: CISubdivisionCodeType


CI: Final[Country] = Country(
    alpha2="CI",
    alpha3="CIV",
    name="Côte d'Ivoire",
    common_name=None,
    official_name="Republic of Côte d'Ivoire",
    subdivisions=[
        CISubdivision(code="CI-AB", name="Abidjan", type_="Autonomous district"),
        CISubdivision(code="CI-BS", name="Bas-Sassandra", type_="District"),
        CISubdivision(code="CI-CM", name="Comoé", type_="District"),
        CISubdivision(code="CI-DN", name="Denguélé", type_="District"),
        CISubdivision(code="CI-GD", name="Gôh-Djiboua", type_="District"),
        CISubdivision(code="CI-LC", name="Lacs", type_="District"),
        CISubdivision(code="CI-LG", name="Lagunes", type_="District"),
        CISubdivision(code="CI-MG", name="Montagnes", type_="District"),
        CISubdivision(code="CI-SM", name="Sassandra-Marahoué", type_="District"),
        CISubdivision(code="CI-SV", name="Savanes", type_="District"),
        CISubdivision(code="CI-VB", name="Vallée du Bandama", type_="District"),
        CISubdivision(code="CI-WR", name="Woroba", type_="District"),
        CISubdivision(code="CI-YM", name="Yamoussoukro", type_="Autonomous district"),
        CISubdivision(code="CI-ZZ", name="Zanzan", type_="District"),
    ],
)
