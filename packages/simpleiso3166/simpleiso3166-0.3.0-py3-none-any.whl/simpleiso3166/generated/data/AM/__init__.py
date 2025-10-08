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

AMSubdivisionCodeType = Literal[
    "AM-AG",  # Aragac̣otn
    "AM-AR",  # Ararat
    "AM-AV",  # Armavir
    "AM-ER",  # Erevan
    "AM-GR",  # Geġark'unik'
    "AM-KT",  # Kotayk'
    "AM-LO",  # Loṙi
    "AM-SH",  # Širak
    "AM-SU",  # Syunik'
    "AM-TV",  # Tavuš
    "AM-VD",  # Vayoć Jor
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class AMSubdivision(Subdivision):
    code: AMSubdivisionCodeType


AM: Final[Country] = Country(
    alpha2="AM",
    alpha3="ARM",
    name="Armenia",
    common_name=None,
    official_name="Republic of Armenia",
    subdivisions=[
        AMSubdivision(code="AM-AG", name="Aragac̣otn", type_="Region"),
        AMSubdivision(code="AM-AR", name="Ararat", type_="Region"),
        AMSubdivision(code="AM-AV", name="Armavir", type_="Region"),
        AMSubdivision(code="AM-ER", name="Erevan", type_="City"),
        AMSubdivision(code="AM-GR", name="Geġark'unik'", type_="Region"),
        AMSubdivision(code="AM-KT", name="Kotayk'", type_="Region"),
        AMSubdivision(code="AM-LO", name="Loṙi", type_="Region"),
        AMSubdivision(code="AM-SH", name="Širak", type_="Region"),
        AMSubdivision(code="AM-SU", name="Syunik'", type_="Region"),
        AMSubdivision(code="AM-TV", name="Tavuš", type_="Region"),
        AMSubdivision(code="AM-VD", name="Vayoć Jor", type_="Region"),
    ],
)
