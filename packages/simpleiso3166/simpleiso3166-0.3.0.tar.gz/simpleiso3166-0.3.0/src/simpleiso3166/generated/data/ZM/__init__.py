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

ZMSubdivisionCodeType = Literal[
    "ZM-01",  # Western
    "ZM-02",  # Central
    "ZM-03",  # Eastern
    "ZM-04",  # Luapula
    "ZM-05",  # Northern
    "ZM-06",  # North-Western
    "ZM-07",  # Southern
    "ZM-08",  # Copperbelt
    "ZM-09",  # Lusaka
    "ZM-10",  # Muchinga
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class ZMSubdivision(Subdivision):
    code: ZMSubdivisionCodeType


ZM: Final[Country] = Country(
    alpha2="ZM",
    alpha3="ZMB",
    name="Zambia",
    common_name=None,
    official_name="Republic of Zambia",
    subdivisions=[
        ZMSubdivision(code="ZM-01", name="Western", type_="Province"),
        ZMSubdivision(code="ZM-02", name="Central", type_="Province"),
        ZMSubdivision(code="ZM-03", name="Eastern", type_="Province"),
        ZMSubdivision(code="ZM-04", name="Luapula", type_="Province"),
        ZMSubdivision(code="ZM-05", name="Northern", type_="Province"),
        ZMSubdivision(code="ZM-06", name="North-Western", type_="Province"),
        ZMSubdivision(code="ZM-07", name="Southern", type_="Province"),
        ZMSubdivision(code="ZM-08", name="Copperbelt", type_="Province"),
        ZMSubdivision(code="ZM-09", name="Lusaka", type_="Province"),
        ZMSubdivision(code="ZM-10", name="Muchinga", type_="Province"),
    ],
)
