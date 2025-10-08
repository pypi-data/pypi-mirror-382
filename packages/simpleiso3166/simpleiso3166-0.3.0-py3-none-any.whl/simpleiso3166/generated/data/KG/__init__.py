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

KGSubdivisionCodeType = Literal[
    "KG-B",  # Batken
    "KG-C",  # Chuyskaya oblast'
    "KG-GB",  # Bishkek Shaary
    "KG-GO",  # Gorod Osh
    "KG-J",  # Dzhalal-Abadskaya oblast'
    "KG-N",  # Naryn
    "KG-O",  # Osh
    "KG-T",  # Talas
    "KG-Y",  # Issyk-Kul'skaja oblast'
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class KGSubdivision(Subdivision):
    code: KGSubdivisionCodeType


KG: Final[Country] = Country(
    alpha2="KG",
    alpha3="KGZ",
    name="Kyrgyzstan",
    common_name=None,
    official_name="Kyrgyz Republic",
    subdivisions=[
        KGSubdivision(code="KG-B", name="Batken", type_="Region"),
        KGSubdivision(code="KG-C", name="Chuyskaya oblast'", type_="Region"),
        KGSubdivision(code="KG-GB", name="Bishkek Shaary", type_="City"),
        KGSubdivision(code="KG-GO", name="Gorod Osh", type_="City"),
        KGSubdivision(code="KG-J", name="Dzhalal-Abadskaya oblast'", type_="Region"),
        KGSubdivision(code="KG-N", name="Naryn", type_="Region"),
        KGSubdivision(code="KG-O", name="Osh", type_="Region"),
        KGSubdivision(code="KG-T", name="Talas", type_="Region"),
        KGSubdivision(code="KG-Y", name="Issyk-Kul'skaja oblast'", type_="Region"),
    ],
)
