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

DMSubdivisionCodeType = Literal[
    "DM-02",  # Saint Andrew
    "DM-03",  # Saint David
    "DM-04",  # Saint George
    "DM-05",  # Saint John
    "DM-06",  # Saint Joseph
    "DM-07",  # Saint Luke
    "DM-08",  # Saint Mark
    "DM-09",  # Saint Patrick
    "DM-10",  # Saint Paul
    "DM-11",  # Saint Peter
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class DMSubdivision(Subdivision):
    code: DMSubdivisionCodeType


DM: Final[Country] = Country(
    alpha2="DM",
    alpha3="DMA",
    name="Dominica",
    common_name=None,
    official_name="Commonwealth of Dominica",
    subdivisions=[
        DMSubdivision(code="DM-02", name="Saint Andrew", type_="Parish"),
        DMSubdivision(code="DM-03", name="Saint David", type_="Parish"),
        DMSubdivision(code="DM-04", name="Saint George", type_="Parish"),
        DMSubdivision(code="DM-05", name="Saint John", type_="Parish"),
        DMSubdivision(code="DM-06", name="Saint Joseph", type_="Parish"),
        DMSubdivision(code="DM-07", name="Saint Luke", type_="Parish"),
        DMSubdivision(code="DM-08", name="Saint Mark", type_="Parish"),
        DMSubdivision(code="DM-09", name="Saint Patrick", type_="Parish"),
        DMSubdivision(code="DM-10", name="Saint Paul", type_="Parish"),
        DMSubdivision(code="DM-11", name="Saint Peter", type_="Parish"),
    ],
)
