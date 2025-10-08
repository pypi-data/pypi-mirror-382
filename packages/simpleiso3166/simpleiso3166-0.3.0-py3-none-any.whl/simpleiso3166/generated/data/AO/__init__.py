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

AOSubdivisionCodeType = Literal[
    "AO-BGO",  # Bengo
    "AO-BGU",  # Benguela
    "AO-BIE",  # Bié
    "AO-CAB",  # Cabinda
    "AO-CCU",  # Cuando Cubango
    "AO-CNN",  # Cunene
    "AO-CNO",  # Cuanza-Norte
    "AO-CUS",  # Cuanza-Sul
    "AO-HUA",  # Huambo
    "AO-HUI",  # Huíla
    "AO-LNO",  # Lunda-Norte
    "AO-LSU",  # Lunda-Sul
    "AO-LUA",  # Luanda
    "AO-MAL",  # Malange
    "AO-MOX",  # Moxico
    "AO-NAM",  # Namibe
    "AO-UIG",  # Uíge
    "AO-ZAI",  # Zaire
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class AOSubdivision(Subdivision):
    code: AOSubdivisionCodeType


AO: Final[Country] = Country(
    alpha2="AO",
    alpha3="AGO",
    name="Angola",
    common_name=None,
    official_name="Republic of Angola",
    subdivisions=[
        AOSubdivision(code="AO-BGO", name="Bengo", type_="Province"),
        AOSubdivision(code="AO-BGU", name="Benguela", type_="Province"),
        AOSubdivision(code="AO-BIE", name="Bié", type_="Province"),
        AOSubdivision(code="AO-CAB", name="Cabinda", type_="Province"),
        AOSubdivision(code="AO-CCU", name="Cuando Cubango", type_="Province"),
        AOSubdivision(code="AO-CNN", name="Cunene", type_="Province"),
        AOSubdivision(code="AO-CNO", name="Cuanza-Norte", type_="Province"),
        AOSubdivision(code="AO-CUS", name="Cuanza-Sul", type_="Province"),
        AOSubdivision(code="AO-HUA", name="Huambo", type_="Province"),
        AOSubdivision(code="AO-HUI", name="Huíla", type_="Province"),
        AOSubdivision(code="AO-LNO", name="Lunda-Norte", type_="Province"),
        AOSubdivision(code="AO-LSU", name="Lunda-Sul", type_="Province"),
        AOSubdivision(code="AO-LUA", name="Luanda", type_="Province"),
        AOSubdivision(code="AO-MAL", name="Malange", type_="Province"),
        AOSubdivision(code="AO-MOX", name="Moxico", type_="Province"),
        AOSubdivision(code="AO-NAM", name="Namibe", type_="Province"),
        AOSubdivision(code="AO-UIG", name="Uíge", type_="Province"),
        AOSubdivision(code="AO-ZAI", name="Zaire", type_="Province"),
    ],
)
