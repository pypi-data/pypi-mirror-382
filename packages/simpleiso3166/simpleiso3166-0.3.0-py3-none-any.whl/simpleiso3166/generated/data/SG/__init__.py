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

SGSubdivisionCodeType = Literal[
    "SG-01",  # Central Singapore
    "SG-02",  # North East
    "SG-03",  # North West
    "SG-04",  # South East
    "SG-05",  # South West
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SGSubdivision(Subdivision):
    code: SGSubdivisionCodeType


SG: Final[Country] = Country(
    alpha2="SG",
    alpha3="SGP",
    name="Singapore",
    common_name=None,
    official_name="Republic of Singapore",
    subdivisions=[
        SGSubdivision(code="SG-01", name="Central Singapore", type_="District"),
        SGSubdivision(code="SG-02", name="North East", type_="District"),
        SGSubdivision(code="SG-03", name="North West", type_="District"),
        SGSubdivision(code="SG-04", name="South East", type_="District"),
        SGSubdivision(code="SG-05", name="South West", type_="District"),
    ],
)
