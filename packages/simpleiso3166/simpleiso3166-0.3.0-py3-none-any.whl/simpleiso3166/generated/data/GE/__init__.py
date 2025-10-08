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

GESubdivisionCodeType = Literal[
    "GE-AB",  # Abkhazia
    "GE-AJ",  # Ajaria
    "GE-GU",  # Guria
    "GE-IM",  # Imereti
    "GE-KA",  # K'akheti
    "GE-KK",  # Kvemo Kartli
    "GE-MM",  # Mtskheta-Mtianeti
    "GE-RL",  # Rach'a-Lechkhumi-Kvemo Svaneti
    "GE-SJ",  # Samtskhe-Javakheti
    "GE-SK",  # Shida Kartli
    "GE-SZ",  # Samegrelo-Zemo Svaneti
    "GE-TB",  # Tbilisi
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class GESubdivision(Subdivision):
    code: GESubdivisionCodeType


GE: Final[Country] = Country(
    alpha2="GE",
    alpha3="GEO",
    name="Georgia",
    common_name=None,
    official_name=None,
    subdivisions=[
        GESubdivision(code="GE-AB", name="Abkhazia", type_="Autonomous republic"),
        GESubdivision(code="GE-AJ", name="Ajaria", type_="Autonomous republic"),
        GESubdivision(code="GE-GU", name="Guria", type_="Region"),
        GESubdivision(code="GE-IM", name="Imereti", type_="Region"),
        GESubdivision(code="GE-KA", name="K'akheti", type_="Region"),
        GESubdivision(code="GE-KK", name="Kvemo Kartli", type_="Region"),
        GESubdivision(code="GE-MM", name="Mtskheta-Mtianeti", type_="Region"),
        GESubdivision(code="GE-RL", name="Rach'a-Lechkhumi-Kvemo Svaneti", type_="Region"),
        GESubdivision(code="GE-SJ", name="Samtskhe-Javakheti", type_="Region"),
        GESubdivision(code="GE-SK", name="Shida Kartli", type_="Region"),
        GESubdivision(code="GE-SZ", name="Samegrelo-Zemo Svaneti", type_="Region"),
        GESubdivision(code="GE-TB", name="Tbilisi", type_="City"),
    ],
)
