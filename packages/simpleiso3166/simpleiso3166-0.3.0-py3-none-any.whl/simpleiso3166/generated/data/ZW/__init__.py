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

ZWSubdivisionCodeType = Literal[
    "ZW-BU",  # Bulawayo
    "ZW-HA",  # Harare
    "ZW-MA",  # Manicaland
    "ZW-MC",  # Mashonaland Central
    "ZW-ME",  # Mashonaland East
    "ZW-MI",  # Midlands
    "ZW-MN",  # Matabeleland North
    "ZW-MS",  # Matabeleland South
    "ZW-MV",  # Masvingo
    "ZW-MW",  # Mashonaland West
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class ZWSubdivision(Subdivision):
    code: ZWSubdivisionCodeType


ZW: Final[Country] = Country(
    alpha2="ZW",
    alpha3="ZWE",
    name="Zimbabwe",
    common_name=None,
    official_name="Republic of Zimbabwe",
    subdivisions=[
        ZWSubdivision(code="ZW-BU", name="Bulawayo", type_="Province"),
        ZWSubdivision(code="ZW-HA", name="Harare", type_="Province"),
        ZWSubdivision(code="ZW-MA", name="Manicaland", type_="Province"),
        ZWSubdivision(code="ZW-MC", name="Mashonaland Central", type_="Province"),
        ZWSubdivision(code="ZW-ME", name="Mashonaland East", type_="Province"),
        ZWSubdivision(code="ZW-MI", name="Midlands", type_="Province"),
        ZWSubdivision(code="ZW-MN", name="Matabeleland North", type_="Province"),
        ZWSubdivision(code="ZW-MS", name="Matabeleland South", type_="Province"),
        ZWSubdivision(code="ZW-MV", name="Masvingo", type_="Province"),
        ZWSubdivision(code="ZW-MW", name="Mashonaland West", type_="Province"),
    ],
)
