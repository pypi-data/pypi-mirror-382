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

KISubdivisionCodeType = Literal[
    "KI-G",  # Gilbert Islands
    "KI-L",  # Line Islands
    "KI-P",  # Phoenix Islands
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class KISubdivision(Subdivision):
    code: KISubdivisionCodeType


KI: Final[Country] = Country(
    alpha2="KI",
    alpha3="KIR",
    name="Kiribati",
    common_name=None,
    official_name="Republic of Kiribati",
    subdivisions=[
        KISubdivision(code="KI-G", name="Gilbert Islands", type_="Group of islands (20 inhabited islands)"),
        KISubdivision(code="KI-L", name="Line Islands", type_="Group of islands (20 inhabited islands)"),
        KISubdivision(code="KI-P", name="Phoenix Islands", type_="Group of islands (20 inhabited islands)"),
    ],
)
