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

DKSubdivisionCodeType = Literal[
    "DK-81",  # Nordjylland
    "DK-82",  # Midtjylland
    "DK-83",  # Syddanmark
    "DK-84",  # Hovedstaden
    "DK-85",  # Sjælland
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class DKSubdivision(Subdivision):
    code: DKSubdivisionCodeType


DK: Final[Country] = Country(
    alpha2="DK",
    alpha3="DNK",
    name="Denmark",
    common_name=None,
    official_name="Kingdom of Denmark",
    subdivisions=[
        DKSubdivision(code="DK-81", name="Nordjylland", type_="Region"),
        DKSubdivision(code="DK-82", name="Midtjylland", type_="Region"),
        DKSubdivision(code="DK-83", name="Syddanmark", type_="Region"),
        DKSubdivision(code="DK-84", name="Hovedstaden", type_="Region"),
        DKSubdivision(code="DK-85", name="Sjælland", type_="Region"),
    ],
)
