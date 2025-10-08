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

BQSubdivisionCodeType = Literal[
    "BQ-BO",  # Bonaire
    "BQ-SA",  # Saba
    "BQ-SE",  # Sint Eustatius
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BQSubdivision(Subdivision):
    code: BQSubdivisionCodeType


BQ: Final[Country] = Country(
    alpha2="BQ",
    alpha3="BES",
    name="Bonaire, Sint Eustatius and Saba",
    common_name=None,
    official_name="Bonaire, Sint Eustatius and Saba",
    subdivisions=[
        BQSubdivision(code="BQ-BO", name="Bonaire", type_="Special municipality"),
        BQSubdivision(code="BQ-SA", name="Saba", type_="Special municipality"),
        BQSubdivision(code="BQ-SE", name="Sint Eustatius", type_="Special municipality"),
    ],
)
