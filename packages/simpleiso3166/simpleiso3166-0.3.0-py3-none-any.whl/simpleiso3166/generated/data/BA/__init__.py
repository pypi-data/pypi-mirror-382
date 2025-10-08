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

BASubdivisionCodeType = Literal[
    "BA-BIH",  # Federacija Bosne i Hercegovine
    "BA-BRC",  # Brčko distrikt
    "BA-SRP",  # Republika Srpska
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BASubdivision(Subdivision):
    code: BASubdivisionCodeType


BA: Final[Country] = Country(
    alpha2="BA",
    alpha3="BIH",
    name="Bosnia and Herzegovina",
    common_name=None,
    official_name="Republic of Bosnia and Herzegovina",
    subdivisions=[
        BASubdivision(code="BA-BIH", name="Federacija Bosne i Hercegovine", type_="Entity"),
        BASubdivision(code="BA-BRC", name="Brčko distrikt", type_="District with special status"),
        BASubdivision(code="BA-SRP", name="Republika Srpska", type_="Entity"),
    ],
)
