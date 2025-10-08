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

VCSubdivisionCodeType = Literal[
    "VC-01",  # Charlotte
    "VC-02",  # Saint Andrew
    "VC-03",  # Saint David
    "VC-04",  # Saint George
    "VC-05",  # Saint Patrick
    "VC-06",  # Grenadines
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class VCSubdivision(Subdivision):
    code: VCSubdivisionCodeType


VC: Final[Country] = Country(
    alpha2="VC",
    alpha3="VCT",
    name="Saint Vincent and the Grenadines",
    common_name=None,
    official_name=None,
    subdivisions=[
        VCSubdivision(code="VC-01", name="Charlotte", type_="Parish"),
        VCSubdivision(code="VC-02", name="Saint Andrew", type_="Parish"),
        VCSubdivision(code="VC-03", name="Saint David", type_="Parish"),
        VCSubdivision(code="VC-04", name="Saint George", type_="Parish"),
        VCSubdivision(code="VC-05", name="Saint Patrick", type_="Parish"),
        VCSubdivision(code="VC-06", name="Grenadines", type_="Parish"),
    ],
)
