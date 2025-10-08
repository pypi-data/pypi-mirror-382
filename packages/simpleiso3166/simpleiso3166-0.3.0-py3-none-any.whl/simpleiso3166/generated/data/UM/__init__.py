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

UMSubdivisionCodeType = Literal[
    "UM-67",  # Johnston Atoll
    "UM-71",  # Midway Islands
    "UM-76",  # Navassa Island
    "UM-79",  # Wake Island
    "UM-81",  # Baker Island
    "UM-84",  # Howland Island
    "UM-86",  # Jarvis Island
    "UM-89",  # Kingman Reef
    "UM-95",  # Palmyra Atoll
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class UMSubdivision(Subdivision):
    code: UMSubdivisionCodeType


UM: Final[Country] = Country(
    alpha2="UM",
    alpha3="UMI",
    name="United States Minor Outlying Islands",
    common_name=None,
    official_name=None,
    subdivisions=[
        UMSubdivision(code="UM-67", name="Johnston Atoll", type_="Islands, groups of islands"),
        UMSubdivision(code="UM-71", name="Midway Islands", type_="Islands, groups of islands"),
        UMSubdivision(code="UM-76", name="Navassa Island", type_="Islands, groups of islands"),
        UMSubdivision(code="UM-79", name="Wake Island", type_="Islands, groups of islands"),
        UMSubdivision(code="UM-81", name="Baker Island", type_="Islands, groups of islands"),
        UMSubdivision(code="UM-84", name="Howland Island", type_="Islands, groups of islands"),
        UMSubdivision(code="UM-86", name="Jarvis Island", type_="Islands, groups of islands"),
        UMSubdivision(code="UM-89", name="Kingman Reef", type_="Islands, groups of islands"),
        UMSubdivision(code="UM-95", name="Palmyra Atoll", type_="Islands, groups of islands"),
    ],
)
