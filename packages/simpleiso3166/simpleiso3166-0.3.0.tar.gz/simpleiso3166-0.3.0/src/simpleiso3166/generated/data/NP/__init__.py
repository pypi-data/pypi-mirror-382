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

NPSubdivisionCodeType = Literal[
    "NP-P1",  # Koshi
    "NP-P2",  # Madhesh
    "NP-P3",  # Bagmati
    "NP-P4",  # Gandaki
    "NP-P5",  # Lumbini
    "NP-P6",  # Karnali
    "NP-P7",  # Sudurpashchim
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class NPSubdivision(Subdivision):
    code: NPSubdivisionCodeType


NP: Final[Country] = Country(
    alpha2="NP",
    alpha3="NPL",
    name="Nepal",
    common_name=None,
    official_name="Federal Democratic Republic of Nepal",
    subdivisions=[
        NPSubdivision(code="NP-P1", name="Koshi", type_="Province"),
        NPSubdivision(code="NP-P2", name="Madhesh", type_="Province"),
        NPSubdivision(code="NP-P3", name="Bagmati", type_="Province"),
        NPSubdivision(code="NP-P4", name="Gandaki", type_="Province"),
        NPSubdivision(code="NP-P5", name="Lumbini", type_="Province"),
        NPSubdivision(code="NP-P6", name="Karnali", type_="Province"),
        NPSubdivision(code="NP-P7", name="Sudurpashchim", type_="Province"),
    ],
)
