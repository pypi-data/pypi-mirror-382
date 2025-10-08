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

SKSubdivisionCodeType = Literal[
    "SK-BC",  # Banskobystrický kraj
    "SK-BL",  # Bratislavský kraj
    "SK-KI",  # Košický kraj
    "SK-NI",  # Nitriansky kraj
    "SK-PV",  # Prešovský kraj
    "SK-TA",  # Trnavský kraj
    "SK-TC",  # Trenčiansky kraj
    "SK-ZI",  # Žilinský kraj
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SKSubdivision(Subdivision):
    code: SKSubdivisionCodeType


SK: Final[Country] = Country(
    alpha2="SK",
    alpha3="SVK",
    name="Slovakia",
    common_name=None,
    official_name="Slovak Republic",
    subdivisions=[
        SKSubdivision(code="SK-BC", name="Banskobystrický kraj", type_="Region"),
        SKSubdivision(code="SK-BL", name="Bratislavský kraj", type_="Region"),
        SKSubdivision(code="SK-KI", name="Košický kraj", type_="Region"),
        SKSubdivision(code="SK-NI", name="Nitriansky kraj", type_="Region"),
        SKSubdivision(code="SK-PV", name="Prešovský kraj", type_="Region"),
        SKSubdivision(code="SK-TA", name="Trnavský kraj", type_="Region"),
        SKSubdivision(code="SK-TC", name="Trenčiansky kraj", type_="Region"),
        SKSubdivision(code="SK-ZI", name="Žilinský kraj", type_="Region"),
    ],
)
