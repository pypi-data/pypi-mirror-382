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

KNSubdivisionCodeType = Literal[
    "KN-01",  # Christ Church Nichola Town
    "KN-02",  # Saint Anne Sandy Point
    "KN-03",  # Saint George Basseterre
    "KN-04",  # Saint George Gingerland
    "KN-05",  # Saint James Windward
    "KN-06",  # Saint John Capisterre
    "KN-07",  # Saint John Figtree
    "KN-08",  # Saint Mary Cayon
    "KN-09",  # Saint Paul Capisterre
    "KN-10",  # Saint Paul Charlestown
    "KN-11",  # Saint Peter Basseterre
    "KN-12",  # Saint Thomas Lowland
    "KN-13",  # Saint Thomas Middle Island
    "KN-15",  # Trinity Palmetto Point
    "KN-K",  # Saint Kitts
    "KN-N",  # Nevis
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class KNSubdivision(Subdivision):
    code: KNSubdivisionCodeType


KN: Final[Country] = Country(
    alpha2="KN",
    alpha3="KNA",
    name="Saint Kitts and Nevis",
    common_name=None,
    official_name=None,
    subdivisions=[
        KNSubdivision(code="KN-01", name="Christ Church Nichola Town", type_="Parish"),
        KNSubdivision(code="KN-02", name="Saint Anne Sandy Point", type_="Parish"),
        KNSubdivision(code="KN-03", name="Saint George Basseterre", type_="Parish"),
        KNSubdivision(code="KN-04", name="Saint George Gingerland", type_="Parish"),
        KNSubdivision(code="KN-05", name="Saint James Windward", type_="Parish"),
        KNSubdivision(code="KN-06", name="Saint John Capisterre", type_="Parish"),
        KNSubdivision(code="KN-07", name="Saint John Figtree", type_="Parish"),
        KNSubdivision(code="KN-08", name="Saint Mary Cayon", type_="Parish"),
        KNSubdivision(code="KN-09", name="Saint Paul Capisterre", type_="Parish"),
        KNSubdivision(code="KN-10", name="Saint Paul Charlestown", type_="Parish"),
        KNSubdivision(code="KN-11", name="Saint Peter Basseterre", type_="Parish"),
        KNSubdivision(code="KN-12", name="Saint Thomas Lowland", type_="Parish"),
        KNSubdivision(code="KN-13", name="Saint Thomas Middle Island", type_="Parish"),
        KNSubdivision(code="KN-15", name="Trinity Palmetto Point", type_="Parish"),
        KNSubdivision(code="KN-K", name="Saint Kitts", type_="State"),
        KNSubdivision(code="KN-N", name="Nevis", type_="State"),
    ],
)
