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

BISubdivisionCodeType = Literal[
    "BI-BB",  # Bubanza
    "BI-BL",  # Bujumbura Rural
    "BI-BM",  # Bujumbura Mairie
    "BI-BR",  # Bururi
    "BI-CA",  # Cankuzo
    "BI-CI",  # Cibitoke
    "BI-GI",  # Gitega
    "BI-KI",  # Kirundo
    "BI-KR",  # Karuzi
    "BI-KY",  # Kayanza
    "BI-MA",  # Makamba
    "BI-MU",  # Muramvya
    "BI-MW",  # Mwaro
    "BI-MY",  # Muyinga
    "BI-NG",  # Ngozi
    "BI-RM",  # Rumonge
    "BI-RT",  # Rutana
    "BI-RY",  # Ruyigi
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BISubdivision(Subdivision):
    code: BISubdivisionCodeType


BI: Final[Country] = Country(
    alpha2="BI",
    alpha3="BDI",
    name="Burundi",
    common_name=None,
    official_name="Republic of Burundi",
    subdivisions=[
        BISubdivision(code="BI-BB", name="Bubanza", type_="Province"),
        BISubdivision(code="BI-BL", name="Bujumbura Rural", type_="Province"),
        BISubdivision(code="BI-BM", name="Bujumbura Mairie", type_="Province"),
        BISubdivision(code="BI-BR", name="Bururi", type_="Province"),
        BISubdivision(code="BI-CA", name="Cankuzo", type_="Province"),
        BISubdivision(code="BI-CI", name="Cibitoke", type_="Province"),
        BISubdivision(code="BI-GI", name="Gitega", type_="Province"),
        BISubdivision(code="BI-KI", name="Kirundo", type_="Province"),
        BISubdivision(code="BI-KR", name="Karuzi", type_="Province"),
        BISubdivision(code="BI-KY", name="Kayanza", type_="Province"),
        BISubdivision(code="BI-MA", name="Makamba", type_="Province"),
        BISubdivision(code="BI-MU", name="Muramvya", type_="Province"),
        BISubdivision(code="BI-MW", name="Mwaro", type_="Province"),
        BISubdivision(code="BI-MY", name="Muyinga", type_="Province"),
        BISubdivision(code="BI-NG", name="Ngozi", type_="Province"),
        BISubdivision(code="BI-RM", name="Rumonge", type_="Province"),
        BISubdivision(code="BI-RT", name="Rutana", type_="Province"),
        BISubdivision(code="BI-RY", name="Ruyigi", type_="Province"),
    ],
)
