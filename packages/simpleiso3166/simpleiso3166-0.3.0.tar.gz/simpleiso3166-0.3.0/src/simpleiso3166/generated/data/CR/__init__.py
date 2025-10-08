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

CRSubdivisionCodeType = Literal[
    "CR-A",  # Alajuela
    "CR-C",  # Cartago
    "CR-G",  # Guanacaste
    "CR-H",  # Heredia
    "CR-L",  # Limón
    "CR-P",  # Puntarenas
    "CR-SJ",  # San José
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class CRSubdivision(Subdivision):
    code: CRSubdivisionCodeType


CR: Final[Country] = Country(
    alpha2="CR",
    alpha3="CRI",
    name="Costa Rica",
    common_name=None,
    official_name="Republic of Costa Rica",
    subdivisions=[
        CRSubdivision(code="CR-A", name="Alajuela", type_="Province"),
        CRSubdivision(code="CR-C", name="Cartago", type_="Province"),
        CRSubdivision(code="CR-G", name="Guanacaste", type_="Province"),
        CRSubdivision(code="CR-H", name="Heredia", type_="Province"),
        CRSubdivision(code="CR-L", name="Limón", type_="Province"),
        CRSubdivision(code="CR-P", name="Puntarenas", type_="Province"),
        CRSubdivision(code="CR-SJ", name="San José", type_="Province"),
    ],
)
