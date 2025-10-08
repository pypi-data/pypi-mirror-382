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

AGSubdivisionCodeType = Literal[
    "AG-03",  # Saint George
    "AG-04",  # Saint John
    "AG-05",  # Saint Mary
    "AG-06",  # Saint Paul
    "AG-07",  # Saint Peter
    "AG-08",  # Saint Philip
    "AG-10",  # Barbuda
    "AG-11",  # Redonda
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class AGSubdivision(Subdivision):
    code: AGSubdivisionCodeType


AG: Final[Country] = Country(
    alpha2="AG",
    alpha3="ATG",
    name="Antigua and Barbuda",
    common_name=None,
    official_name=None,
    subdivisions=[
        AGSubdivision(code="AG-03", name="Saint George", type_="Parish"),
        AGSubdivision(code="AG-04", name="Saint John", type_="Parish"),
        AGSubdivision(code="AG-05", name="Saint Mary", type_="Parish"),
        AGSubdivision(code="AG-06", name="Saint Paul", type_="Parish"),
        AGSubdivision(code="AG-07", name="Saint Peter", type_="Parish"),
        AGSubdivision(code="AG-08", name="Saint Philip", type_="Parish"),
        AGSubdivision(code="AG-10", name="Barbuda", type_="Dependency"),
        AGSubdivision(code="AG-11", name="Redonda", type_="Dependency"),
    ],
)
