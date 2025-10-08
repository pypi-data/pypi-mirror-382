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

JMSubdivisionCodeType = Literal[
    "JM-01",  # Kingston
    "JM-02",  # Saint Andrew
    "JM-03",  # Saint Thomas
    "JM-04",  # Portland
    "JM-05",  # Saint Mary
    "JM-06",  # Saint Ann
    "JM-07",  # Trelawny
    "JM-08",  # Saint James
    "JM-09",  # Hanover
    "JM-10",  # Westmoreland
    "JM-11",  # Saint Elizabeth
    "JM-12",  # Manchester
    "JM-13",  # Clarendon
    "JM-14",  # Saint Catherine
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class JMSubdivision(Subdivision):
    code: JMSubdivisionCodeType


JM: Final[Country] = Country(
    alpha2="JM",
    alpha3="JAM",
    name="Jamaica",
    common_name=None,
    official_name=None,
    subdivisions=[
        JMSubdivision(code="JM-01", name="Kingston", type_="Parish"),
        JMSubdivision(code="JM-02", name="Saint Andrew", type_="Parish"),
        JMSubdivision(code="JM-03", name="Saint Thomas", type_="Parish"),
        JMSubdivision(code="JM-04", name="Portland", type_="Parish"),
        JMSubdivision(code="JM-05", name="Saint Mary", type_="Parish"),
        JMSubdivision(code="JM-06", name="Saint Ann", type_="Parish"),
        JMSubdivision(code="JM-07", name="Trelawny", type_="Parish"),
        JMSubdivision(code="JM-08", name="Saint James", type_="Parish"),
        JMSubdivision(code="JM-09", name="Hanover", type_="Parish"),
        JMSubdivision(code="JM-10", name="Westmoreland", type_="Parish"),
        JMSubdivision(code="JM-11", name="Saint Elizabeth", type_="Parish"),
        JMSubdivision(code="JM-12", name="Manchester", type_="Parish"),
        JMSubdivision(code="JM-13", name="Clarendon", type_="Parish"),
        JMSubdivision(code="JM-14", name="Saint Catherine", type_="Parish"),
    ],
)
