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

RWSubdivisionCodeType = Literal[
    "RW-01",  # City of Kigali
    "RW-02",  # Eastern
    "RW-03",  # Northern
    "RW-04",  # Western
    "RW-05",  # Southern
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class RWSubdivision(Subdivision):
    code: RWSubdivisionCodeType


RW: Final[Country] = Country(
    alpha2="RW",
    alpha3="RWA",
    name="Rwanda",
    common_name=None,
    official_name="Rwandese Republic",
    subdivisions=[
        RWSubdivision(code="RW-01", name="City of Kigali", type_="City"),
        RWSubdivision(code="RW-02", name="Eastern", type_="Province"),
        RWSubdivision(code="RW-03", name="Northern", type_="Province"),
        RWSubdivision(code="RW-04", name="Western", type_="Province"),
        RWSubdivision(code="RW-05", name="Southern", type_="Province"),
    ],
)
