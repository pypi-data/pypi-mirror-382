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

CFSubdivisionCodeType = Literal[
    "CF-AC",  # Ouham
    "CF-BB",  # Bamingui-Bangoran
    "CF-BGF",  # Bangui
    "CF-BK",  # Basse-Kotto
    "CF-HK",  # Haute-Kotto
    "CF-HM",  # Haut-Mbomou
    "CF-HS",  # Haute-Sangha / Mambéré-Kadéï
    "CF-KB",  # Gribingui
    "CF-KG",  # Kémo-Gribingui
    "CF-LB",  # Lobaye
    "CF-MB",  # Mbomou
    "CF-MP",  # Ombella-Mpoko
    "CF-NM",  # Nana-Mambéré
    "CF-OP",  # Ouham-Pendé
    "CF-SE",  # Sangha
    "CF-UK",  # Ouaka
    "CF-VK",  # Vakaga
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class CFSubdivision(Subdivision):
    code: CFSubdivisionCodeType


CF: Final[Country] = Country(
    alpha2="CF",
    alpha3="CAF",
    name="Central African Republic",
    common_name=None,
    official_name=None,
    subdivisions=[
        CFSubdivision(code="CF-AC", name="Ouham", type_="Prefecture"),
        CFSubdivision(code="CF-BB", name="Bamingui-Bangoran", type_="Prefecture"),
        CFSubdivision(code="CF-BGF", name="Bangui", type_="Commune"),
        CFSubdivision(code="CF-BK", name="Basse-Kotto", type_="Prefecture"),
        CFSubdivision(code="CF-HK", name="Haute-Kotto", type_="Prefecture"),
        CFSubdivision(code="CF-HM", name="Haut-Mbomou", type_="Prefecture"),
        CFSubdivision(code="CF-HS", name="Haute-Sangha / Mambéré-Kadéï", type_="Prefecture"),
        CFSubdivision(code="CF-KB", name="Gribingui", type_="Economic prefecture"),
        CFSubdivision(code="CF-KG", name="Kémo-Gribingui", type_="Prefecture"),
        CFSubdivision(code="CF-LB", name="Lobaye", type_="Prefecture"),
        CFSubdivision(code="CF-MB", name="Mbomou", type_="Prefecture"),
        CFSubdivision(code="CF-MP", name="Ombella-Mpoko", type_="Prefecture"),
        CFSubdivision(code="CF-NM", name="Nana-Mambéré", type_="Prefecture"),
        CFSubdivision(code="CF-OP", name="Ouham-Pendé", type_="Prefecture"),
        CFSubdivision(code="CF-SE", name="Sangha", type_="Economic prefecture"),
        CFSubdivision(code="CF-UK", name="Ouaka", type_="Prefecture"),
        CFSubdivision(code="CF-VK", name="Vakaga", type_="Prefecture"),
    ],
)
