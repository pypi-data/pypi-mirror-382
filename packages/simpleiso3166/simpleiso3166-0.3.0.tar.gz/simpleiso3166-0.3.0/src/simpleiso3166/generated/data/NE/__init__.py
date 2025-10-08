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

NESubdivisionCodeType = Literal[
    "NE-1",  # Agadez
    "NE-2",  # Diffa
    "NE-3",  # Dosso
    "NE-4",  # Maradi
    "NE-5",  # Tahoua
    "NE-6",  # Tillabéri
    "NE-7",  # Zinder
    "NE-8",  # Niamey
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class NESubdivision(Subdivision):
    code: NESubdivisionCodeType


NE: Final[Country] = Country(
    alpha2="NE",
    alpha3="NER",
    name="Niger",
    common_name=None,
    official_name="Republic of the Niger",
    subdivisions=[
        NESubdivision(code="NE-1", name="Agadez", type_="Region"),
        NESubdivision(code="NE-2", name="Diffa", type_="Region"),
        NESubdivision(code="NE-3", name="Dosso", type_="Region"),
        NESubdivision(code="NE-4", name="Maradi", type_="Region"),
        NESubdivision(code="NE-5", name="Tahoua", type_="Region"),
        NESubdivision(code="NE-6", name="Tillabéri", type_="Region"),
        NESubdivision(code="NE-7", name="Zinder", type_="Region"),
        NESubdivision(code="NE-8", name="Niamey", type_="Urban community"),
    ],
)
