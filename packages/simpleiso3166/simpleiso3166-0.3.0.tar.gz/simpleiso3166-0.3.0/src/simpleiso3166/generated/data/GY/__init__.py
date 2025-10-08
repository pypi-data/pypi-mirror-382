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

GYSubdivisionCodeType = Literal[
    "GY-BA",  # Barima-Waini
    "GY-CU",  # Cuyuni-Mazaruni
    "GY-DE",  # Demerara-Mahaica
    "GY-EB",  # East Berbice-Corentyne
    "GY-ES",  # Essequibo Islands-West Demerara
    "GY-MA",  # Mahaica-Berbice
    "GY-PM",  # Pomeroon-Supenaam
    "GY-PT",  # Potaro-Siparuni
    "GY-UD",  # Upper Demerara-Berbice
    "GY-UT",  # Upper Takutu-Upper Essequibo
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class GYSubdivision(Subdivision):
    code: GYSubdivisionCodeType


GY: Final[Country] = Country(
    alpha2="GY",
    alpha3="GUY",
    name="Guyana",
    common_name=None,
    official_name="Republic of Guyana",
    subdivisions=[
        GYSubdivision(code="GY-BA", name="Barima-Waini", type_="Region"),
        GYSubdivision(code="GY-CU", name="Cuyuni-Mazaruni", type_="Region"),
        GYSubdivision(code="GY-DE", name="Demerara-Mahaica", type_="Region"),
        GYSubdivision(code="GY-EB", name="East Berbice-Corentyne", type_="Region"),
        GYSubdivision(code="GY-ES", name="Essequibo Islands-West Demerara", type_="Region"),
        GYSubdivision(code="GY-MA", name="Mahaica-Berbice", type_="Region"),
        GYSubdivision(code="GY-PM", name="Pomeroon-Supenaam", type_="Region"),
        GYSubdivision(code="GY-PT", name="Potaro-Siparuni", type_="Region"),
        GYSubdivision(code="GY-UD", name="Upper Demerara-Berbice", type_="Region"),
        GYSubdivision(code="GY-UT", name="Upper Takutu-Upper Essequibo", type_="Region"),
    ],
)
