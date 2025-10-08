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

SZSubdivisionCodeType = Literal[
    "SZ-HH",  # Hhohho
    "SZ-LU",  # Lubombo
    "SZ-MA",  # Manzini
    "SZ-SH",  # Shiselweni
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SZSubdivision(Subdivision):
    code: SZSubdivisionCodeType


SZ: Final[Country] = Country(
    alpha2="SZ",
    alpha3="SWZ",
    name="Eswatini",
    common_name=None,
    official_name="Kingdom of Eswatini",
    subdivisions=[
        SZSubdivision(code="SZ-HH", name="Hhohho", type_="Region"),
        SZSubdivision(code="SZ-LU", name="Lubombo", type_="Region"),
        SZSubdivision(code="SZ-MA", name="Manzini", type_="Region"),
        SZSubdivision(code="SZ-SH", name="Shiselweni", type_="Region"),
    ],
)
