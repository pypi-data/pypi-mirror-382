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

SSSubdivisionCodeType = Literal[
    "SS-BN",  # Northern Bahr el Ghazal
    "SS-BW",  # Western Bahr el Ghazal
    "SS-EC",  # Central Equatoria
    "SS-EE",  # Eastern Equatoria
    "SS-EW",  # Western Equatoria
    "SS-JG",  # Jonglei
    "SS-LK",  # Lakes
    "SS-NU",  # Upper Nile
    "SS-UY",  # Unity
    "SS-WR",  # Warrap
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SSSubdivision(Subdivision):
    code: SSSubdivisionCodeType


SS: Final[Country] = Country(
    alpha2="SS",
    alpha3="SSD",
    name="South Sudan",
    common_name=None,
    official_name="Republic of South Sudan",
    subdivisions=[
        SSSubdivision(code="SS-BN", name="Northern Bahr el Ghazal", type_="State"),
        SSSubdivision(code="SS-BW", name="Western Bahr el Ghazal", type_="State"),
        SSSubdivision(code="SS-EC", name="Central Equatoria", type_="State"),
        SSSubdivision(code="SS-EE", name="Eastern Equatoria", type_="State"),
        SSSubdivision(code="SS-EW", name="Western Equatoria", type_="State"),
        SSSubdivision(code="SS-JG", name="Jonglei", type_="State"),
        SSSubdivision(code="SS-LK", name="Lakes", type_="State"),
        SSSubdivision(code="SS-NU", name="Upper Nile", type_="State"),
        SSSubdivision(code="SS-UY", name="Unity", type_="State"),
        SSSubdivision(code="SS-WR", name="Warrap", type_="State"),
    ],
)
