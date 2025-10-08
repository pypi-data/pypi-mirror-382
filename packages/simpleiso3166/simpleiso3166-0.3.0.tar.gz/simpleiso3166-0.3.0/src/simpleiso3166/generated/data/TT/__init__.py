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

TTSubdivisionCodeType = Literal[
    "TT-ARI",  # Arima
    "TT-CHA",  # Chaguanas
    "TT-CTT",  # Couva-Tabaquite-Talparo
    "TT-DMN",  # Diego Martin
    "TT-MRC",  # Mayaro-Rio Claro
    "TT-PED",  # Penal-Debe
    "TT-POS",  # Port of Spain
    "TT-PRT",  # Princes Town
    "TT-PTF",  # Point Fortin
    "TT-SFO",  # San Fernando
    "TT-SGE",  # Sangre Grande
    "TT-SIP",  # Siparia
    "TT-SJL",  # San Juan-Laventille
    "TT-TOB",  # Tobago
    "TT-TUP",  # Tunapuna-Piarco
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class TTSubdivision(Subdivision):
    code: TTSubdivisionCodeType


TT: Final[Country] = Country(
    alpha2="TT",
    alpha3="TTO",
    name="Trinidad and Tobago",
    common_name=None,
    official_name="Republic of Trinidad and Tobago",
    subdivisions=[
        TTSubdivision(code="TT-ARI", name="Arima", type_="Borough"),
        TTSubdivision(code="TT-CHA", name="Chaguanas", type_="Borough"),
        TTSubdivision(code="TT-CTT", name="Couva-Tabaquite-Talparo", type_="Region"),
        TTSubdivision(code="TT-DMN", name="Diego Martin", type_="Region"),
        TTSubdivision(code="TT-MRC", name="Mayaro-Rio Claro", type_="Region"),
        TTSubdivision(code="TT-PED", name="Penal-Debe", type_="Region"),
        TTSubdivision(code="TT-POS", name="Port of Spain", type_="City"),
        TTSubdivision(code="TT-PRT", name="Princes Town", type_="Region"),
        TTSubdivision(code="TT-PTF", name="Point Fortin", type_="Borough"),
        TTSubdivision(code="TT-SFO", name="San Fernando", type_="City"),
        TTSubdivision(code="TT-SGE", name="Sangre Grande", type_="Region"),
        TTSubdivision(code="TT-SIP", name="Siparia", type_="Region"),
        TTSubdivision(code="TT-SJL", name="San Juan-Laventille", type_="Region"),
        TTSubdivision(code="TT-TOB", name="Tobago", type_="Ward"),
        TTSubdivision(code="TT-TUP", name="Tunapuna-Piarco", type_="Region"),
    ],
)
