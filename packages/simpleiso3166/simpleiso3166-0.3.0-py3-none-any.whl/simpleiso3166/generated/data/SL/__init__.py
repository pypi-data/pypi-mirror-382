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

SLSubdivisionCodeType = Literal[
    "SL-E",  # Eastern
    "SL-N",  # Northern
    "SL-NW",  # North Western
    "SL-S",  # Southern
    "SL-W",  # Western Area (Freetown)
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SLSubdivision(Subdivision):
    code: SLSubdivisionCodeType


SL: Final[Country] = Country(
    alpha2="SL",
    alpha3="SLE",
    name="Sierra Leone",
    common_name=None,
    official_name="Republic of Sierra Leone",
    subdivisions=[
        SLSubdivision(code="SL-E", name="Eastern", type_="Province"),
        SLSubdivision(code="SL-N", name="Northern", type_="Province"),
        SLSubdivision(code="SL-NW", name="North Western", type_="Province"),
        SLSubdivision(code="SL-S", name="Southern", type_="Province"),
        SLSubdivision(code="SL-W", name="Western Area (Freetown)", type_="Area"),
    ],
)
