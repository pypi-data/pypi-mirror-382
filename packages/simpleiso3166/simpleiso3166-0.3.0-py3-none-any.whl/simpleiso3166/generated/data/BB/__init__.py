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

BBSubdivisionCodeType = Literal[
    "BB-01",  # Christ Church
    "BB-02",  # Saint Andrew
    "BB-03",  # Saint George
    "BB-04",  # Saint James
    "BB-05",  # Saint John
    "BB-06",  # Saint Joseph
    "BB-07",  # Saint Lucy
    "BB-08",  # Saint Michael
    "BB-09",  # Saint Peter
    "BB-10",  # Saint Philip
    "BB-11",  # Saint Thomas
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BBSubdivision(Subdivision):
    code: BBSubdivisionCodeType


BB: Final[Country] = Country(
    alpha2="BB",
    alpha3="BRB",
    name="Barbados",
    common_name=None,
    official_name=None,
    subdivisions=[
        BBSubdivision(code="BB-01", name="Christ Church", type_="Parish"),
        BBSubdivision(code="BB-02", name="Saint Andrew", type_="Parish"),
        BBSubdivision(code="BB-03", name="Saint George", type_="Parish"),
        BBSubdivision(code="BB-04", name="Saint James", type_="Parish"),
        BBSubdivision(code="BB-05", name="Saint John", type_="Parish"),
        BBSubdivision(code="BB-06", name="Saint Joseph", type_="Parish"),
        BBSubdivision(code="BB-07", name="Saint Lucy", type_="Parish"),
        BBSubdivision(code="BB-08", name="Saint Michael", type_="Parish"),
        BBSubdivision(code="BB-09", name="Saint Peter", type_="Parish"),
        BBSubdivision(code="BB-10", name="Saint Philip", type_="Parish"),
        BBSubdivision(code="BB-11", name="Saint Thomas", type_="Parish"),
    ],
)
