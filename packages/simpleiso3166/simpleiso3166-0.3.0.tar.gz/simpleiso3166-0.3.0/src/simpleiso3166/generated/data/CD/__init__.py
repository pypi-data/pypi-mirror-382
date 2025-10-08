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

CDSubdivisionCodeType = Literal[
    "CD-BC",  # Kongo Central
    "CD-BU",  # Bas-Uélé
    "CD-EQ",  # Équateur
    "CD-HK",  # Haut-Katanga
    "CD-HL",  # Haut-Lomami
    "CD-HU",  # Haut-Uélé
    "CD-IT",  # Ituri
    "CD-KC",  # Kasaï Central
    "CD-KE",  # Kasaï Oriental
    "CD-KG",  # Kwango
    "CD-KL",  # Kwilu
    "CD-KN",  # Kinshasa
    "CD-KS",  # Kasaï
    "CD-LO",  # Lomami
    "CD-LU",  # Lualaba
    "CD-MA",  # Maniema
    "CD-MN",  # Mai-Ndombe
    "CD-MO",  # Mongala
    "CD-NK",  # Nord-Kivu
    "CD-NU",  # Nord-Ubangi
    "CD-SA",  # Sankuru
    "CD-SK",  # Sud-Kivu
    "CD-SU",  # Sud-Ubangi
    "CD-TA",  # Tanganyika
    "CD-TO",  # Tshopo
    "CD-TU",  # Tshuapa
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class CDSubdivision(Subdivision):
    code: CDSubdivisionCodeType


CD: Final[Country] = Country(
    alpha2="CD",
    alpha3="COD",
    name="Congo, The Democratic Republic of the",
    common_name=None,
    official_name=None,
    subdivisions=[
        CDSubdivision(code="CD-BC", name="Kongo Central", type_="Province"),
        CDSubdivision(code="CD-BU", name="Bas-Uélé", type_="Province"),
        CDSubdivision(code="CD-EQ", name="Équateur", type_="Province"),
        CDSubdivision(code="CD-HK", name="Haut-Katanga", type_="Province"),
        CDSubdivision(code="CD-HL", name="Haut-Lomami", type_="Province"),
        CDSubdivision(code="CD-HU", name="Haut-Uélé", type_="Province"),
        CDSubdivision(code="CD-IT", name="Ituri", type_="Province"),
        CDSubdivision(code="CD-KC", name="Kasaï Central", type_="Province"),
        CDSubdivision(code="CD-KE", name="Kasaï Oriental", type_="Province"),
        CDSubdivision(code="CD-KG", name="Kwango", type_="Province"),
        CDSubdivision(code="CD-KL", name="Kwilu", type_="Province"),
        CDSubdivision(code="CD-KN", name="Kinshasa", type_="City"),
        CDSubdivision(code="CD-KS", name="Kasaï", type_="Province"),
        CDSubdivision(code="CD-LO", name="Lomami", type_="Province"),
        CDSubdivision(code="CD-LU", name="Lualaba", type_="Province"),
        CDSubdivision(code="CD-MA", name="Maniema", type_="Province"),
        CDSubdivision(code="CD-MN", name="Mai-Ndombe", type_="Province"),
        CDSubdivision(code="CD-MO", name="Mongala", type_="Province"),
        CDSubdivision(code="CD-NK", name="Nord-Kivu", type_="Province"),
        CDSubdivision(code="CD-NU", name="Nord-Ubangi", type_="Province"),
        CDSubdivision(code="CD-SA", name="Sankuru", type_="Province"),
        CDSubdivision(code="CD-SK", name="Sud-Kivu", type_="Province"),
        CDSubdivision(code="CD-SU", name="Sud-Ubangi", type_="Province"),
        CDSubdivision(code="CD-TA", name="Tanganyika", type_="Province"),
        CDSubdivision(code="CD-TO", name="Tshopo", type_="Province"),
        CDSubdivision(code="CD-TU", name="Tshuapa", type_="Province"),
    ],
)
