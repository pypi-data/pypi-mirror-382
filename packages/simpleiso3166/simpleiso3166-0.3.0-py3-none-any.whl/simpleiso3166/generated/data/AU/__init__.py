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

AUSubdivisionCodeType = Literal[
    "AU-ACT",  # Australian Capital Territory
    "AU-NSW",  # New South Wales
    "AU-NT",  # Northern Territory
    "AU-QLD",  # Queensland
    "AU-SA",  # South Australia
    "AU-TAS",  # Tasmania
    "AU-VIC",  # Victoria
    "AU-WA",  # Western Australia
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class AUSubdivision(Subdivision):
    code: AUSubdivisionCodeType


AU: Final[Country] = Country(
    alpha2="AU",
    alpha3="AUS",
    name="Australia",
    common_name=None,
    official_name=None,
    subdivisions=[
        AUSubdivision(code="AU-ACT", name="Australian Capital Territory", type_="Territory"),
        AUSubdivision(code="AU-NSW", name="New South Wales", type_="State"),
        AUSubdivision(code="AU-NT", name="Northern Territory", type_="Territory"),
        AUSubdivision(code="AU-QLD", name="Queensland", type_="State"),
        AUSubdivision(code="AU-SA", name="South Australia", type_="State"),
        AUSubdivision(code="AU-TAS", name="Tasmania", type_="State"),
        AUSubdivision(code="AU-VIC", name="Victoria", type_="State"),
        AUSubdivision(code="AU-WA", name="Western Australia", type_="State"),
    ],
)
