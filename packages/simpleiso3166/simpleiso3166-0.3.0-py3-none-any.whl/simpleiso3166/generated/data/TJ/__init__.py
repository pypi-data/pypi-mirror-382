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

TJSubdivisionCodeType = Literal[
    "TJ-DU",  # Dushanbe
    "TJ-GB",  # Kŭhistoni Badakhshon
    "TJ-KT",  # Khatlon
    "TJ-RA",  # nohiyahoi tobei jumhurí
    "TJ-SU",  # Sughd
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class TJSubdivision(Subdivision):
    code: TJSubdivisionCodeType


TJ: Final[Country] = Country(
    alpha2="TJ",
    alpha3="TJK",
    name="Tajikistan",
    common_name=None,
    official_name="Republic of Tajikistan",
    subdivisions=[
        TJSubdivision(code="TJ-DU", name="Dushanbe", type_="Capital territory"),
        TJSubdivision(code="TJ-GB", name="Kŭhistoni Badakhshon", type_="Autonomous region"),
        TJSubdivision(code="TJ-KT", name="Khatlon", type_="Region"),
        TJSubdivision(code="TJ-RA", name="nohiyahoi tobei jumhurí", type_="Districts under republic administration"),
        TJSubdivision(code="TJ-SU", name="Sughd", type_="Region"),
    ],
)
