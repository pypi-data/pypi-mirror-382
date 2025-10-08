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

TOSubdivisionCodeType = Literal[
    "TO-01",  # 'Eua
    "TO-02",  # Ha'apai
    "TO-03",  # Niuas
    "TO-04",  # Tongatapu
    "TO-05",  # Vava'u
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class TOSubdivision(Subdivision):
    code: TOSubdivisionCodeType


TO: Final[Country] = Country(
    alpha2="TO",
    alpha3="TON",
    name="Tonga",
    common_name=None,
    official_name="Kingdom of Tonga",
    subdivisions=[
        TOSubdivision(code="TO-01", name="'Eua", type_="Division"),
        TOSubdivision(code="TO-02", name="Ha'apai", type_="Division"),
        TOSubdivision(code="TO-03", name="Niuas", type_="Division"),
        TOSubdivision(code="TO-04", name="Tongatapu", type_="Division"),
        TOSubdivision(code="TO-05", name="Vava'u", type_="Division"),
    ],
)
