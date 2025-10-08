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

GASubdivisionCodeType = Literal[
    "GA-1",  # Estuaire
    "GA-2",  # Haut-Ogooué
    "GA-3",  # Moyen-Ogooué
    "GA-4",  # Ngounié
    "GA-5",  # Nyanga
    "GA-6",  # Ogooué-Ivindo
    "GA-7",  # Ogooué-Lolo
    "GA-8",  # Ogooué-Maritime
    "GA-9",  # Woleu-Ntem
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class GASubdivision(Subdivision):
    code: GASubdivisionCodeType


GA: Final[Country] = Country(
    alpha2="GA",
    alpha3="GAB",
    name="Gabon",
    common_name=None,
    official_name="Gabonese Republic",
    subdivisions=[
        GASubdivision(code="GA-1", name="Estuaire", type_="Province"),
        GASubdivision(code="GA-2", name="Haut-Ogooué", type_="Province"),
        GASubdivision(code="GA-3", name="Moyen-Ogooué", type_="Province"),
        GASubdivision(code="GA-4", name="Ngounié", type_="Province"),
        GASubdivision(code="GA-5", name="Nyanga", type_="Province"),
        GASubdivision(code="GA-6", name="Ogooué-Ivindo", type_="Province"),
        GASubdivision(code="GA-7", name="Ogooué-Lolo", type_="Province"),
        GASubdivision(code="GA-8", name="Ogooué-Maritime", type_="Province"),
        GASubdivision(code="GA-9", name="Woleu-Ntem", type_="Province"),
    ],
)
