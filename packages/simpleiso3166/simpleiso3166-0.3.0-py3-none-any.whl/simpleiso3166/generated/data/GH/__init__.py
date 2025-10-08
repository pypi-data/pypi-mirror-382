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

GHSubdivisionCodeType = Literal[
    "GH-AA",  # Greater Accra
    "GH-AF",  # Ahafo
    "GH-AH",  # Ashanti
    "GH-BE",  # Bono East
    "GH-BO",  # Bono
    "GH-CP",  # Central
    "GH-EP",  # Eastern
    "GH-NE",  # North East
    "GH-NP",  # Northern
    "GH-OT",  # Oti
    "GH-SV",  # Savannah
    "GH-TV",  # Volta
    "GH-UE",  # Upper East
    "GH-UW",  # Upper West
    "GH-WN",  # Western North
    "GH-WP",  # Western
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class GHSubdivision(Subdivision):
    code: GHSubdivisionCodeType


GH: Final[Country] = Country(
    alpha2="GH",
    alpha3="GHA",
    name="Ghana",
    common_name=None,
    official_name="Republic of Ghana",
    subdivisions=[
        GHSubdivision(code="GH-AA", name="Greater Accra", type_="Region"),
        GHSubdivision(code="GH-AF", name="Ahafo", type_="Region"),
        GHSubdivision(code="GH-AH", name="Ashanti", type_="Region"),
        GHSubdivision(code="GH-BE", name="Bono East", type_="Region"),
        GHSubdivision(code="GH-BO", name="Bono", type_="Region"),
        GHSubdivision(code="GH-CP", name="Central", type_="Region"),
        GHSubdivision(code="GH-EP", name="Eastern", type_="Region"),
        GHSubdivision(code="GH-NE", name="North East", type_="Region"),
        GHSubdivision(code="GH-NP", name="Northern", type_="Region"),
        GHSubdivision(code="GH-OT", name="Oti", type_="Region"),
        GHSubdivision(code="GH-SV", name="Savannah", type_="Region"),
        GHSubdivision(code="GH-TV", name="Volta", type_="Region"),
        GHSubdivision(code="GH-UE", name="Upper East", type_="Region"),
        GHSubdivision(code="GH-UW", name="Upper West", type_="Region"),
        GHSubdivision(code="GH-WN", name="Western North", type_="Region"),
        GHSubdivision(code="GH-WP", name="Western", type_="Region"),
    ],
)
