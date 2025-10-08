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

SBSubdivisionCodeType = Literal[
    "SB-CE",  # Central
    "SB-CH",  # Choiseul
    "SB-CT",  # Capital Territory (Honiara)
    "SB-GU",  # Guadalcanal
    "SB-IS",  # Isabel
    "SB-MK",  # Makira-Ulawa
    "SB-ML",  # Malaita
    "SB-RB",  # Rennell and Bellona
    "SB-TE",  # Temotu
    "SB-WE",  # Western
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SBSubdivision(Subdivision):
    code: SBSubdivisionCodeType


SB: Final[Country] = Country(
    alpha2="SB",
    alpha3="SLB",
    name="Solomon Islands",
    common_name=None,
    official_name=None,
    subdivisions=[
        SBSubdivision(code="SB-CE", name="Central", type_="Province"),
        SBSubdivision(code="SB-CH", name="Choiseul", type_="Province"),
        SBSubdivision(code="SB-CT", name="Capital Territory (Honiara)", type_="Capital territory"),
        SBSubdivision(code="SB-GU", name="Guadalcanal", type_="Province"),
        SBSubdivision(code="SB-IS", name="Isabel", type_="Province"),
        SBSubdivision(code="SB-MK", name="Makira-Ulawa", type_="Province"),
        SBSubdivision(code="SB-ML", name="Malaita", type_="Province"),
        SBSubdivision(code="SB-RB", name="Rennell and Bellona", type_="Province"),
        SBSubdivision(code="SB-TE", name="Temotu", type_="Province"),
        SBSubdivision(code="SB-WE", name="Western", type_="Province"),
    ],
)
