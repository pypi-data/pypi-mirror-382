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

ZASubdivisionCodeType = Literal[
    "ZA-EC",  # Eastern Cape
    "ZA-FS",  # Free State
    "ZA-GP",  # Gauteng
    "ZA-KZN",  # Kwazulu-Natal
    "ZA-LP",  # Limpopo
    "ZA-MP",  # Mpumalanga
    "ZA-NC",  # Northern Cape
    "ZA-NW",  # North-West
    "ZA-WC",  # Western Cape
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class ZASubdivision(Subdivision):
    code: ZASubdivisionCodeType


ZA: Final[Country] = Country(
    alpha2="ZA",
    alpha3="ZAF",
    name="South Africa",
    common_name=None,
    official_name="Republic of South Africa",
    subdivisions=[
        ZASubdivision(code="ZA-EC", name="Eastern Cape", type_="Province"),
        ZASubdivision(code="ZA-FS", name="Free State", type_="Province"),
        ZASubdivision(code="ZA-GP", name="Gauteng", type_="Province"),
        ZASubdivision(code="ZA-KZN", name="Kwazulu-Natal", type_="Province"),
        ZASubdivision(code="ZA-LP", name="Limpopo", type_="Province"),
        ZASubdivision(code="ZA-MP", name="Mpumalanga", type_="Province"),
        ZASubdivision(code="ZA-NC", name="Northern Cape", type_="Province"),
        ZASubdivision(code="ZA-NW", name="North-West", type_="Province"),
        ZASubdivision(code="ZA-WC", name="Western Cape", type_="Province"),
    ],
)
