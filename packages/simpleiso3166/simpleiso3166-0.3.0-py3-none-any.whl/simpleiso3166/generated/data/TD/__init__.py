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

TDSubdivisionCodeType = Literal[
    "TD-BA",  # Batha
    "TD-BG",  # Bahr el Ghazal
    "TD-BO",  # Borkou
    "TD-CB",  # Chari-Baguirmi
    "TD-EE",  # Ennedi-Est
    "TD-EO",  # Ennedi-Ouest
    "TD-GR",  # Guéra
    "TD-HL",  # Hadjer Lamis
    "TD-KA",  # Kanem
    "TD-LC",  # Lac
    "TD-LO",  # Logone-Occidental
    "TD-LR",  # Logone-Oriental
    "TD-MA",  # Mandoul
    "TD-MC",  # Moyen-Chari
    "TD-ME",  # Mayo-Kebbi-Est
    "TD-MO",  # Mayo-Kebbi-Ouest
    "TD-ND",  # Ville de Ndjamena
    "TD-OD",  # Ouaddaï
    "TD-SA",  # Salamat
    "TD-SI",  # Sila
    "TD-TA",  # Tandjilé
    "TD-TI",  # Tibesti
    "TD-WF",  # Wadi Fira
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class TDSubdivision(Subdivision):
    code: TDSubdivisionCodeType


TD: Final[Country] = Country(
    alpha2="TD",
    alpha3="TCD",
    name="Chad",
    common_name=None,
    official_name="Republic of Chad",
    subdivisions=[
        TDSubdivision(code="TD-BA", name="Batha", type_="Province"),
        TDSubdivision(code="TD-BG", name="Bahr el Ghazal", type_="Province"),
        TDSubdivision(code="TD-BO", name="Borkou", type_="Province"),
        TDSubdivision(code="TD-CB", name="Chari-Baguirmi", type_="Province"),
        TDSubdivision(code="TD-EE", name="Ennedi-Est", type_="Province"),
        TDSubdivision(code="TD-EO", name="Ennedi-Ouest", type_="Province"),
        TDSubdivision(code="TD-GR", name="Guéra", type_="Province"),
        TDSubdivision(code="TD-HL", name="Hadjer Lamis", type_="Province"),
        TDSubdivision(code="TD-KA", name="Kanem", type_="Province"),
        TDSubdivision(code="TD-LC", name="Lac", type_="Province"),
        TDSubdivision(code="TD-LO", name="Logone-Occidental", type_="Province"),
        TDSubdivision(code="TD-LR", name="Logone-Oriental", type_="Province"),
        TDSubdivision(code="TD-MA", name="Mandoul", type_="Province"),
        TDSubdivision(code="TD-MC", name="Moyen-Chari", type_="Province"),
        TDSubdivision(code="TD-ME", name="Mayo-Kebbi-Est", type_="Province"),
        TDSubdivision(code="TD-MO", name="Mayo-Kebbi-Ouest", type_="Province"),
        TDSubdivision(code="TD-ND", name="Ville de Ndjamena", type_="Province"),
        TDSubdivision(code="TD-OD", name="Ouaddaï", type_="Province"),
        TDSubdivision(code="TD-SA", name="Salamat", type_="Province"),
        TDSubdivision(code="TD-SI", name="Sila", type_="Province"),
        TDSubdivision(code="TD-TA", name="Tandjilé", type_="Province"),
        TDSubdivision(code="TD-TI", name="Tibesti", type_="Province"),
        TDSubdivision(code="TD-WF", name="Wadi Fira", type_="Province"),
    ],
)
