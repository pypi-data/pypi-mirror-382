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

TLSubdivisionCodeType = Literal[
    "TL-AL",  # Aileu
    "TL-AN",  # Ainaro
    "TL-BA",  # Baucau
    "TL-BO",  # Bobonaro
    "TL-CO",  # Cova Lima
    "TL-DI",  # Díli
    "TL-ER",  # Ermera
    "TL-LA",  # Lautein
    "TL-LI",  # Likisá
    "TL-MF",  # Manufahi
    "TL-MT",  # Manatuto
    "TL-OE",  # Oekusi-Ambenu
    "TL-VI",  # Vikeke
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class TLSubdivision(Subdivision):
    code: TLSubdivisionCodeType


TL: Final[Country] = Country(
    alpha2="TL",
    alpha3="TLS",
    name="Timor-Leste",
    common_name=None,
    official_name="Democratic Republic of Timor-Leste",
    subdivisions=[
        TLSubdivision(code="TL-AL", name="Aileu", type_="Municipality"),
        TLSubdivision(code="TL-AN", name="Ainaro", type_="Municipality"),
        TLSubdivision(code="TL-BA", name="Baucau", type_="Municipality"),
        TLSubdivision(code="TL-BO", name="Bobonaro", type_="Municipality"),
        TLSubdivision(code="TL-CO", name="Cova Lima", type_="Municipality"),
        TLSubdivision(code="TL-DI", name="Díli", type_="Municipality"),
        TLSubdivision(code="TL-ER", name="Ermera", type_="Municipality"),
        TLSubdivision(code="TL-LA", name="Lautein", type_="Municipality"),
        TLSubdivision(code="TL-LI", name="Likisá", type_="Municipality"),
        TLSubdivision(code="TL-MF", name="Manufahi", type_="Municipality"),
        TLSubdivision(code="TL-MT", name="Manatuto", type_="Municipality"),
        TLSubdivision(code="TL-OE", name="Oekusi-Ambenu", type_="Special administrative region"),
        TLSubdivision(code="TL-VI", name="Vikeke", type_="Municipality"),
    ],
)
