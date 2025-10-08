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

TVSubdivisionCodeType = Literal[
    "TV-FUN",  # Funafuti
    "TV-NIT",  # Niutao
    "TV-NKF",  # Nukufetau
    "TV-NKL",  # Nukulaelae
    "TV-NMA",  # Nanumea
    "TV-NMG",  # Nanumaga
    "TV-NUI",  # Nui
    "TV-VAI",  # Vaitupu
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class TVSubdivision(Subdivision):
    code: TVSubdivisionCodeType


TV: Final[Country] = Country(
    alpha2="TV",
    alpha3="TUV",
    name="Tuvalu",
    common_name=None,
    official_name=None,
    subdivisions=[
        TVSubdivision(code="TV-FUN", name="Funafuti", type_="Town council"),
        TVSubdivision(code="TV-NIT", name="Niutao", type_="Island council"),
        TVSubdivision(code="TV-NKF", name="Nukufetau", type_="Island council"),
        TVSubdivision(code="TV-NKL", name="Nukulaelae", type_="Island council"),
        TVSubdivision(code="TV-NMA", name="Nanumea", type_="Island council"),
        TVSubdivision(code="TV-NMG", name="Nanumaga", type_="Island council"),
        TVSubdivision(code="TV-NUI", name="Nui", type_="Island council"),
        TVSubdivision(code="TV-VAI", name="Vaitupu", type_="Island council"),
    ],
)
