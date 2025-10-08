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

GDSubdivisionCodeType = Literal[
    "GD-01",  # Saint Andrew
    "GD-02",  # Saint David
    "GD-03",  # Saint George
    "GD-04",  # Saint John
    "GD-05",  # Saint Mark
    "GD-06",  # Saint Patrick
    "GD-10",  # Southern Grenadine Islands
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class GDSubdivision(Subdivision):
    code: GDSubdivisionCodeType


GD: Final[Country] = Country(
    alpha2="GD",
    alpha3="GRD",
    name="Grenada",
    common_name=None,
    official_name=None,
    subdivisions=[
        GDSubdivision(code="GD-01", name="Saint Andrew", type_="Parish"),
        GDSubdivision(code="GD-02", name="Saint David", type_="Parish"),
        GDSubdivision(code="GD-03", name="Saint George", type_="Parish"),
        GDSubdivision(code="GD-04", name="Saint John", type_="Parish"),
        GDSubdivision(code="GD-05", name="Saint Mark", type_="Parish"),
        GDSubdivision(code="GD-06", name="Saint Patrick", type_="Parish"),
        GDSubdivision(code="GD-10", name="Southern Grenadine Islands", type_="Dependency"),
    ],
)
