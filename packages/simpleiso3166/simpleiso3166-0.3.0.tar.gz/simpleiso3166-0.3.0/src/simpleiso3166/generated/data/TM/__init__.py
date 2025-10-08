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

TMSubdivisionCodeType = Literal[
    "TM-A",  # Ahal
    "TM-B",  # Balkan
    "TM-D",  # Daşoguz
    "TM-L",  # Lebap
    "TM-M",  # Mary
    "TM-S",  # Aşgabat
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class TMSubdivision(Subdivision):
    code: TMSubdivisionCodeType


TM: Final[Country] = Country(
    alpha2="TM",
    alpha3="TKM",
    name="Turkmenistan",
    common_name=None,
    official_name=None,
    subdivisions=[
        TMSubdivision(code="TM-A", name="Ahal", type_="Region"),
        TMSubdivision(code="TM-B", name="Balkan", type_="Region"),
        TMSubdivision(code="TM-D", name="Daşoguz", type_="Region"),
        TMSubdivision(code="TM-L", name="Lebap", type_="Region"),
        TMSubdivision(code="TM-M", name="Mary", type_="Region"),
        TMSubdivision(code="TM-S", name="Aşgabat", type_="City"),
    ],
)
