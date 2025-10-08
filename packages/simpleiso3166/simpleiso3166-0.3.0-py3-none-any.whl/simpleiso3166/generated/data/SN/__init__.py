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

SNSubdivisionCodeType = Literal[
    "SN-DB",  # Diourbel
    "SN-DK",  # Dakar
    "SN-FK",  # Fatick
    "SN-KA",  # Kaffrine
    "SN-KD",  # Kolda
    "SN-KE",  # Kédougou
    "SN-KL",  # Kaolack
    "SN-LG",  # Louga
    "SN-MT",  # Matam
    "SN-SE",  # Sédhiou
    "SN-SL",  # Saint-Louis
    "SN-TC",  # Tambacounda
    "SN-TH",  # Thiès
    "SN-ZG",  # Ziguinchor
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SNSubdivision(Subdivision):
    code: SNSubdivisionCodeType


SN: Final[Country] = Country(
    alpha2="SN",
    alpha3="SEN",
    name="Senegal",
    common_name=None,
    official_name="Republic of Senegal",
    subdivisions=[
        SNSubdivision(code="SN-DB", name="Diourbel", type_="Region"),
        SNSubdivision(code="SN-DK", name="Dakar", type_="Region"),
        SNSubdivision(code="SN-FK", name="Fatick", type_="Region"),
        SNSubdivision(code="SN-KA", name="Kaffrine", type_="Region"),
        SNSubdivision(code="SN-KD", name="Kolda", type_="Region"),
        SNSubdivision(code="SN-KE", name="Kédougou", type_="Region"),
        SNSubdivision(code="SN-KL", name="Kaolack", type_="Region"),
        SNSubdivision(code="SN-LG", name="Louga", type_="Region"),
        SNSubdivision(code="SN-MT", name="Matam", type_="Region"),
        SNSubdivision(code="SN-SE", name="Sédhiou", type_="Region"),
        SNSubdivision(code="SN-SL", name="Saint-Louis", type_="Region"),
        SNSubdivision(code="SN-TC", name="Tambacounda", type_="Region"),
        SNSubdivision(code="SN-TH", name="Thiès", type_="Region"),
        SNSubdivision(code="SN-ZG", name="Ziguinchor", type_="Region"),
    ],
)
