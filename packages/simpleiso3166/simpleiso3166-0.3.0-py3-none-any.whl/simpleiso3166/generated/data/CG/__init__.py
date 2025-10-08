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

CGSubdivisionCodeType = Literal[
    "CG-11",  # Bouenza
    "CG-12",  # Pool
    "CG-13",  # Sangha
    "CG-14",  # Plateaux
    "CG-15",  # Cuvette-Ouest
    "CG-16",  # Pointe-Noire
    "CG-2",  # Lékoumou
    "CG-5",  # Kouilou
    "CG-7",  # Likouala
    "CG-8",  # Cuvette
    "CG-9",  # Niari
    "CG-BZV",  # Brazzaville
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class CGSubdivision(Subdivision):
    code: CGSubdivisionCodeType


CG: Final[Country] = Country(
    alpha2="CG",
    alpha3="COG",
    name="Congo",
    common_name=None,
    official_name="Republic of the Congo",
    subdivisions=[
        CGSubdivision(code="CG-11", name="Bouenza", type_="Department"),
        CGSubdivision(code="CG-12", name="Pool", type_="Department"),
        CGSubdivision(code="CG-13", name="Sangha", type_="Department"),
        CGSubdivision(code="CG-14", name="Plateaux", type_="Department"),
        CGSubdivision(code="CG-15", name="Cuvette-Ouest", type_="Department"),
        CGSubdivision(code="CG-16", name="Pointe-Noire", type_="Department"),
        CGSubdivision(code="CG-2", name="Lékoumou", type_="Department"),
        CGSubdivision(code="CG-5", name="Kouilou", type_="Department"),
        CGSubdivision(code="CG-7", name="Likouala", type_="Department"),
        CGSubdivision(code="CG-8", name="Cuvette", type_="Department"),
        CGSubdivision(code="CG-9", name="Niari", type_="Department"),
        CGSubdivision(code="CG-BZV", name="Brazzaville", type_="Department"),
    ],
)
