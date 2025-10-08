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

SHSubdivisionCodeType = Literal[
    "SH-AC",  # Ascension
    "SH-HL",  # Saint Helena
    "SH-TA",  # Tristan da Cunha
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SHSubdivision(Subdivision):
    code: SHSubdivisionCodeType


SH: Final[Country] = Country(
    alpha2="SH",
    alpha3="SHN",
    name="Saint Helena, Ascension and Tristan da Cunha",
    common_name=None,
    official_name=None,
    subdivisions=[
        SHSubdivision(code="SH-AC", name="Ascension", type_="Geographical entity"),
        SHSubdivision(code="SH-HL", name="Saint Helena", type_="Geographical entity"),
        SHSubdivision(code="SH-TA", name="Tristan da Cunha", type_="Geographical entity"),
    ],
)
