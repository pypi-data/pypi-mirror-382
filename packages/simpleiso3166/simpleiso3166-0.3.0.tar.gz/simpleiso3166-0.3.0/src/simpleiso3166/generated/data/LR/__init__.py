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

LRSubdivisionCodeType = Literal[
    "LR-BG",  # Bong
    "LR-BM",  # Bomi
    "LR-CM",  # Grand Cape Mount
    "LR-GB",  # Grand Bassa
    "LR-GG",  # Grand Gedeh
    "LR-GK",  # Grand Kru
    "LR-GP",  # Gbarpolu
    "LR-LO",  # Lofa
    "LR-MG",  # Margibi
    "LR-MO",  # Montserrado
    "LR-MY",  # Maryland
    "LR-NI",  # Nimba
    "LR-RG",  # River Gee
    "LR-RI",  # River Cess
    "LR-SI",  # Sinoe
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class LRSubdivision(Subdivision):
    code: LRSubdivisionCodeType


LR: Final[Country] = Country(
    alpha2="LR",
    alpha3="LBR",
    name="Liberia",
    common_name=None,
    official_name="Republic of Liberia",
    subdivisions=[
        LRSubdivision(code="LR-BG", name="Bong", type_="County"),
        LRSubdivision(code="LR-BM", name="Bomi", type_="County"),
        LRSubdivision(code="LR-CM", name="Grand Cape Mount", type_="County"),
        LRSubdivision(code="LR-GB", name="Grand Bassa", type_="County"),
        LRSubdivision(code="LR-GG", name="Grand Gedeh", type_="County"),
        LRSubdivision(code="LR-GK", name="Grand Kru", type_="County"),
        LRSubdivision(code="LR-GP", name="Gbarpolu", type_="County"),
        LRSubdivision(code="LR-LO", name="Lofa", type_="County"),
        LRSubdivision(code="LR-MG", name="Margibi", type_="County"),
        LRSubdivision(code="LR-MO", name="Montserrado", type_="County"),
        LRSubdivision(code="LR-MY", name="Maryland", type_="County"),
        LRSubdivision(code="LR-NI", name="Nimba", type_="County"),
        LRSubdivision(code="LR-RG", name="River Gee", type_="County"),
        LRSubdivision(code="LR-RI", name="River Cess", type_="County"),
        LRSubdivision(code="LR-SI", name="Sinoe", type_="County"),
    ],
)
