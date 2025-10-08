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

ILSubdivisionCodeType = Literal[
    "IL-D",  # Al Janūbī
    "IL-HA",  # H̱efa
    "IL-JM",  # Al Quds
    "IL-M",  # Al Awsaţ
    "IL-TA",  # Tall Abīb
    "IL-Z",  # Ash Shamālī
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class ILSubdivision(Subdivision):
    code: ILSubdivisionCodeType


IL: Final[Country] = Country(
    alpha2="IL",
    alpha3="ISR",
    name="Israel",
    common_name=None,
    official_name="State of Israel",
    subdivisions=[
        ILSubdivision(code="IL-D", name="Al Janūbī", type_="District"),
        ILSubdivision(code="IL-HA", name="H̱efa", type_="District"),
        ILSubdivision(code="IL-JM", name="Al Quds", type_="District"),
        ILSubdivision(code="IL-M", name="Al Awsaţ", type_="District"),
        ILSubdivision(code="IL-TA", name="Tall Abīb", type_="District"),
        ILSubdivision(code="IL-Z", name="Ash Shamālī", type_="District"),
    ],
)
