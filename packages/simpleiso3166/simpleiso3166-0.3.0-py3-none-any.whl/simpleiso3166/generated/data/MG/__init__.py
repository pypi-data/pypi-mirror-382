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

MGSubdivisionCodeType = Literal[
    "MG-A",  # Toamasina
    "MG-D",  # Antsiranana
    "MG-F",  # Fianarantsoa
    "MG-M",  # Mahajanga
    "MG-T",  # Antananarivo
    "MG-U",  # Toliara
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MGSubdivision(Subdivision):
    code: MGSubdivisionCodeType


MG: Final[Country] = Country(
    alpha2="MG",
    alpha3="MDG",
    name="Madagascar",
    common_name=None,
    official_name="Republic of Madagascar",
    subdivisions=[
        MGSubdivision(code="MG-A", name="Toamasina", type_="Province"),
        MGSubdivision(code="MG-D", name="Antsiranana", type_="Province"),
        MGSubdivision(code="MG-F", name="Fianarantsoa", type_="Province"),
        MGSubdivision(code="MG-M", name="Mahajanga", type_="Province"),
        MGSubdivision(code="MG-T", name="Antananarivo", type_="Province"),
        MGSubdivision(code="MG-U", name="Toliara", type_="Province"),
    ],
)
