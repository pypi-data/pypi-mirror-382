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

UYSubdivisionCodeType = Literal[
    "UY-AR",  # Artigas
    "UY-CA",  # Canelones
    "UY-CL",  # Cerro Largo
    "UY-CO",  # Colonia
    "UY-DU",  # Durazno
    "UY-FD",  # Florida
    "UY-FS",  # Flores
    "UY-LA",  # Lavalleja
    "UY-MA",  # Maldonado
    "UY-MO",  # Montevideo
    "UY-PA",  # Paysandú
    "UY-RN",  # Río Negro
    "UY-RO",  # Rocha
    "UY-RV",  # Rivera
    "UY-SA",  # Salto
    "UY-SJ",  # San José
    "UY-SO",  # Soriano
    "UY-TA",  # Tacuarembó
    "UY-TT",  # Treinta y Tres
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class UYSubdivision(Subdivision):
    code: UYSubdivisionCodeType


UY: Final[Country] = Country(
    alpha2="UY",
    alpha3="URY",
    name="Uruguay",
    common_name=None,
    official_name="Eastern Republic of Uruguay",
    subdivisions=[
        UYSubdivision(code="UY-AR", name="Artigas", type_="Department"),
        UYSubdivision(code="UY-CA", name="Canelones", type_="Department"),
        UYSubdivision(code="UY-CL", name="Cerro Largo", type_="Department"),
        UYSubdivision(code="UY-CO", name="Colonia", type_="Department"),
        UYSubdivision(code="UY-DU", name="Durazno", type_="Department"),
        UYSubdivision(code="UY-FD", name="Florida", type_="Department"),
        UYSubdivision(code="UY-FS", name="Flores", type_="Department"),
        UYSubdivision(code="UY-LA", name="Lavalleja", type_="Department"),
        UYSubdivision(code="UY-MA", name="Maldonado", type_="Department"),
        UYSubdivision(code="UY-MO", name="Montevideo", type_="Department"),
        UYSubdivision(code="UY-PA", name="Paysandú", type_="Department"),
        UYSubdivision(code="UY-RN", name="Río Negro", type_="Department"),
        UYSubdivision(code="UY-RO", name="Rocha", type_="Department"),
        UYSubdivision(code="UY-RV", name="Rivera", type_="Department"),
        UYSubdivision(code="UY-SA", name="Salto", type_="Department"),
        UYSubdivision(code="UY-SJ", name="San José", type_="Department"),
        UYSubdivision(code="UY-SO", name="Soriano", type_="Department"),
        UYSubdivision(code="UY-TA", name="Tacuarembó", type_="Department"),
        UYSubdivision(code="UY-TT", name="Treinta y Tres", type_="Department"),
    ],
)
