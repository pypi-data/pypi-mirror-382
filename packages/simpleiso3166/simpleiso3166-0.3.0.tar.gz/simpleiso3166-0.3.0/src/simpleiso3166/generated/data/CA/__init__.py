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

CASubdivisionCodeType = Literal[
    "CA-AB",  # Alberta
    "CA-BC",  # British Columbia
    "CA-MB",  # Manitoba
    "CA-NB",  # New Brunswick
    "CA-NL",  # Newfoundland and Labrador
    "CA-NS",  # Nova Scotia
    "CA-NT",  # Northwest Territories
    "CA-NU",  # Nunavut
    "CA-ON",  # Ontario
    "CA-PE",  # Prince Edward Island
    "CA-QC",  # Quebec
    "CA-SK",  # Saskatchewan
    "CA-YT",  # Yukon
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class CASubdivision(Subdivision):
    code: CASubdivisionCodeType


CA: Final[Country] = Country(
    alpha2="CA",
    alpha3="CAN",
    name="Canada",
    common_name=None,
    official_name=None,
    subdivisions=[
        CASubdivision(code="CA-AB", name="Alberta", type_="Province"),
        CASubdivision(code="CA-BC", name="British Columbia", type_="Province"),
        CASubdivision(code="CA-MB", name="Manitoba", type_="Province"),
        CASubdivision(code="CA-NB", name="New Brunswick", type_="Province"),
        CASubdivision(code="CA-NL", name="Newfoundland and Labrador", type_="Province"),
        CASubdivision(code="CA-NS", name="Nova Scotia", type_="Province"),
        CASubdivision(code="CA-NT", name="Northwest Territories", type_="Territory"),
        CASubdivision(code="CA-NU", name="Nunavut", type_="Territory"),
        CASubdivision(code="CA-ON", name="Ontario", type_="Province"),
        CASubdivision(code="CA-PE", name="Prince Edward Island", type_="Province"),
        CASubdivision(code="CA-QC", name="Quebec", type_="Province"),
        CASubdivision(code="CA-SK", name="Saskatchewan", type_="Province"),
        CASubdivision(code="CA-YT", name="Yukon", type_="Territory"),
    ],
)
