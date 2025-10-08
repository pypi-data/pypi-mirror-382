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

BNSubdivisionCodeType = Literal[
    "BN-BE",  # Belait
    "BN-BM",  # Brunei-Muara
    "BN-TE",  # Temburong
    "BN-TU",  # Tutong
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BNSubdivision(Subdivision):
    code: BNSubdivisionCodeType


BN: Final[Country] = Country(
    alpha2="BN",
    alpha3="BRN",
    name="Brunei Darussalam",
    common_name=None,
    official_name=None,
    subdivisions=[
        BNSubdivision(code="BN-BE", name="Belait", type_="District"),
        BNSubdivision(code="BN-BM", name="Brunei-Muara", type_="District"),
        BNSubdivision(code="BN-TE", name="Temburong", type_="District"),
        BNSubdivision(code="BN-TU", name="Tutong", type_="District"),
    ],
)
