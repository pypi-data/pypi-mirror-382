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

BOSubdivisionCodeType = Literal[
    "BO-B",  # El Beni
    "BO-C",  # Cochabamba
    "BO-H",  # Chuquisaca
    "BO-L",  # La Paz
    "BO-N",  # Pando
    "BO-O",  # Oruro
    "BO-P",  # Potosí
    "BO-S",  # Santa Cruz
    "BO-T",  # Tarija
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BOSubdivision(Subdivision):
    code: BOSubdivisionCodeType


BO: Final[Country] = Country(
    alpha2="BO",
    alpha3="BOL",
    name="Bolivia, Plurinational State of",
    common_name="Bolivia",
    official_name="Plurinational State of Bolivia",
    subdivisions=[
        BOSubdivision(code="BO-B", name="El Beni", type_="Department"),
        BOSubdivision(code="BO-C", name="Cochabamba", type_="Department"),
        BOSubdivision(code="BO-H", name="Chuquisaca", type_="Department"),
        BOSubdivision(code="BO-L", name="La Paz", type_="Department"),
        BOSubdivision(code="BO-N", name="Pando", type_="Department"),
        BOSubdivision(code="BO-O", name="Oruro", type_="Department"),
        BOSubdivision(code="BO-P", name="Potosí", type_="Department"),
        BOSubdivision(code="BO-S", name="Santa Cruz", type_="Department"),
        BOSubdivision(code="BO-T", name="Tarija", type_="Department"),
    ],
)
