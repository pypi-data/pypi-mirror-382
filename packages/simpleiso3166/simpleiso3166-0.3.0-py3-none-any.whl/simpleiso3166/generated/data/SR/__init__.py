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

SRSubdivisionCodeType = Literal[
    "SR-BR",  # Brokopondo
    "SR-CM",  # Commewijne
    "SR-CR",  # Coronie
    "SR-MA",  # Marowijne
    "SR-NI",  # Nickerie
    "SR-PM",  # Paramaribo
    "SR-PR",  # Para
    "SR-SA",  # Saramacca
    "SR-SI",  # Sipaliwini
    "SR-WA",  # Wanica
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SRSubdivision(Subdivision):
    code: SRSubdivisionCodeType


SR: Final[Country] = Country(
    alpha2="SR",
    alpha3="SUR",
    name="Suriname",
    common_name=None,
    official_name="Republic of Suriname",
    subdivisions=[
        SRSubdivision(code="SR-BR", name="Brokopondo", type_="District"),
        SRSubdivision(code="SR-CM", name="Commewijne", type_="District"),
        SRSubdivision(code="SR-CR", name="Coronie", type_="District"),
        SRSubdivision(code="SR-MA", name="Marowijne", type_="District"),
        SRSubdivision(code="SR-NI", name="Nickerie", type_="District"),
        SRSubdivision(code="SR-PM", name="Paramaribo", type_="District"),
        SRSubdivision(code="SR-PR", name="Para", type_="District"),
        SRSubdivision(code="SR-SA", name="Saramacca", type_="District"),
        SRSubdivision(code="SR-SI", name="Sipaliwini", type_="District"),
        SRSubdivision(code="SR-WA", name="Wanica", type_="District"),
    ],
)
