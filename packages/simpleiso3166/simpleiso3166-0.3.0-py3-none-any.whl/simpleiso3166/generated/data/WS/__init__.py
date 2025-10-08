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

WSSubdivisionCodeType = Literal[
    "WS-AA",  # A'ana
    "WS-AL",  # Aiga-i-le-Tai
    "WS-AT",  # Atua
    "WS-FA",  # Fa'asaleleaga
    "WS-GE",  # Gaga'emauga
    "WS-GI",  # Gagaifomauga
    "WS-PA",  # Palauli
    "WS-SA",  # Satupa'itea
    "WS-TU",  # Tuamasaga
    "WS-VF",  # Va'a-o-Fonoti
    "WS-VS",  # Vaisigano
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class WSSubdivision(Subdivision):
    code: WSSubdivisionCodeType


WS: Final[Country] = Country(
    alpha2="WS",
    alpha3="WSM",
    name="Samoa",
    common_name=None,
    official_name="Independent State of Samoa",
    subdivisions=[
        WSSubdivision(code="WS-AA", name="A'ana", type_="District"),
        WSSubdivision(code="WS-AL", name="Aiga-i-le-Tai", type_="District"),
        WSSubdivision(code="WS-AT", name="Atua", type_="District"),
        WSSubdivision(code="WS-FA", name="Fa'asaleleaga", type_="District"),
        WSSubdivision(code="WS-GE", name="Gaga'emauga", type_="District"),
        WSSubdivision(code="WS-GI", name="Gagaifomauga", type_="District"),
        WSSubdivision(code="WS-PA", name="Palauli", type_="District"),
        WSSubdivision(code="WS-SA", name="Satupa'itea", type_="District"),
        WSSubdivision(code="WS-TU", name="Tuamasaga", type_="District"),
        WSSubdivision(code="WS-VF", name="Va'a-o-Fonoti", type_="District"),
        WSSubdivision(code="WS-VS", name="Vaisigano", type_="District"),
    ],
)
