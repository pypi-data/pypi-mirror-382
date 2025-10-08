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

MHSubdivisionCodeType = Literal[
    "MH-ALK",  # Ailuk
    "MH-ALL",  # Ailinglaplap
    "MH-ARN",  # Arno
    "MH-AUR",  # Aur
    "MH-EBO",  # Ebon
    "MH-ENI",  # Enewetak & Ujelang
    "MH-JAB",  # Jabat
    "MH-JAL",  # Jaluit
    "MH-KIL",  # Bikini & Kili
    "MH-KWA",  # Kwajalein
    "MH-L",  # Ralik chain
    "MH-LAE",  # Lae
    "MH-LIB",  # Lib
    "MH-LIK",  # Likiep
    "MH-MAJ",  # Majuro
    "MH-MAL",  # Maloelap
    "MH-MEJ",  # Mejit
    "MH-MIL",  # Mili
    "MH-NMK",  # Namdrik
    "MH-NMU",  # Namu
    "MH-RON",  # Rongelap
    "MH-T",  # Ratak chain
    "MH-UJA",  # Ujae
    "MH-UTI",  # Utrik
    "MH-WTH",  # Wotho
    "MH-WTJ",  # Wotje
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MHSubdivision(Subdivision):
    code: MHSubdivisionCodeType


MH: Final[Country] = Country(
    alpha2="MH",
    alpha3="MHL",
    name="Marshall Islands",
    common_name=None,
    official_name="Republic of the Marshall Islands",
    subdivisions=[
        MHSubdivision(code="MH-ALK", name="Ailuk", type_="Municipality"),
        MHSubdivision(code="MH-ALL", name="Ailinglaplap", type_="Municipality"),
        MHSubdivision(code="MH-ARN", name="Arno", type_="Municipality"),
        MHSubdivision(code="MH-AUR", name="Aur", type_="Municipality"),
        MHSubdivision(code="MH-EBO", name="Ebon", type_="Municipality"),
        MHSubdivision(code="MH-ENI", name="Enewetak & Ujelang", type_="Municipality"),
        MHSubdivision(code="MH-JAB", name="Jabat", type_="Municipality"),
        MHSubdivision(code="MH-JAL", name="Jaluit", type_="Municipality"),
        MHSubdivision(code="MH-KIL", name="Bikini & Kili", type_="Municipality"),
        MHSubdivision(code="MH-KWA", name="Kwajalein", type_="Municipality"),
        MHSubdivision(code="MH-L", name="Ralik chain", type_="Chain (of islands)"),
        MHSubdivision(code="MH-LAE", name="Lae", type_="Municipality"),
        MHSubdivision(code="MH-LIB", name="Lib", type_="Municipality"),
        MHSubdivision(code="MH-LIK", name="Likiep", type_="Municipality"),
        MHSubdivision(code="MH-MAJ", name="Majuro", type_="Municipality"),
        MHSubdivision(code="MH-MAL", name="Maloelap", type_="Municipality"),
        MHSubdivision(code="MH-MEJ", name="Mejit", type_="Municipality"),
        MHSubdivision(code="MH-MIL", name="Mili", type_="Municipality"),
        MHSubdivision(code="MH-NMK", name="Namdrik", type_="Municipality"),
        MHSubdivision(code="MH-NMU", name="Namu", type_="Municipality"),
        MHSubdivision(code="MH-RON", name="Rongelap", type_="Municipality"),
        MHSubdivision(code="MH-T", name="Ratak chain", type_="Chain (of islands)"),
        MHSubdivision(code="MH-UJA", name="Ujae", type_="Municipality"),
        MHSubdivision(code="MH-UTI", name="Utrik", type_="Municipality"),
        MHSubdivision(code="MH-WTH", name="Wotho", type_="Municipality"),
        MHSubdivision(code="MH-WTJ", name="Wotje", type_="Municipality"),
    ],
)
