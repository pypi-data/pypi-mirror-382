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

BZSubdivisionCodeType = Literal[
    "BZ-BZ",  # Belize
    "BZ-CY",  # Cayo
    "BZ-CZL",  # Corozal
    "BZ-OW",  # Orange Walk
    "BZ-SC",  # Stann Creek
    "BZ-TOL",  # Toledo
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BZSubdivision(Subdivision):
    code: BZSubdivisionCodeType


BZ: Final[Country] = Country(
    alpha2="BZ",
    alpha3="BLZ",
    name="Belize",
    common_name=None,
    official_name=None,
    subdivisions=[
        BZSubdivision(code="BZ-BZ", name="Belize", type_="District"),
        BZSubdivision(code="BZ-CY", name="Cayo", type_="District"),
        BZSubdivision(code="BZ-CZL", name="Corozal", type_="District"),
        BZSubdivision(code="BZ-OW", name="Orange Walk", type_="District"),
        BZSubdivision(code="BZ-SC", name="Stann Creek", type_="District"),
        BZSubdivision(code="BZ-TOL", name="Toledo", type_="District"),
    ],
)
