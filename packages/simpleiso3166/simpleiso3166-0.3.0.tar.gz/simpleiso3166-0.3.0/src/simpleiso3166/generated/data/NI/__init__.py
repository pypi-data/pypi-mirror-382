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

NISubdivisionCodeType = Literal[
    "NI-AN",  # Costa Caribe Norte
    "NI-AS",  # Costa Caribe Sur
    "NI-BO",  # Boaco
    "NI-CA",  # Carazo
    "NI-CI",  # Chinandega
    "NI-CO",  # Chontales
    "NI-ES",  # Estelí
    "NI-GR",  # Granada
    "NI-JI",  # Jinotega
    "NI-LE",  # León
    "NI-MD",  # Madriz
    "NI-MN",  # Managua
    "NI-MS",  # Masaya
    "NI-MT",  # Matagalpa
    "NI-NS",  # Nueva Segovia
    "NI-RI",  # Rivas
    "NI-SJ",  # Río San Juan
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class NISubdivision(Subdivision):
    code: NISubdivisionCodeType


NI: Final[Country] = Country(
    alpha2="NI",
    alpha3="NIC",
    name="Nicaragua",
    common_name=None,
    official_name="Republic of Nicaragua",
    subdivisions=[
        NISubdivision(code="NI-AN", name="Costa Caribe Norte", type_="Autonomous region"),
        NISubdivision(code="NI-AS", name="Costa Caribe Sur", type_="Autonomous region"),
        NISubdivision(code="NI-BO", name="Boaco", type_="Department"),
        NISubdivision(code="NI-CA", name="Carazo", type_="Department"),
        NISubdivision(code="NI-CI", name="Chinandega", type_="Department"),
        NISubdivision(code="NI-CO", name="Chontales", type_="Department"),
        NISubdivision(code="NI-ES", name="Estelí", type_="Department"),
        NISubdivision(code="NI-GR", name="Granada", type_="Department"),
        NISubdivision(code="NI-JI", name="Jinotega", type_="Department"),
        NISubdivision(code="NI-LE", name="León", type_="Department"),
        NISubdivision(code="NI-MD", name="Madriz", type_="Department"),
        NISubdivision(code="NI-MN", name="Managua", type_="Department"),
        NISubdivision(code="NI-MS", name="Masaya", type_="Department"),
        NISubdivision(code="NI-MT", name="Matagalpa", type_="Department"),
        NISubdivision(code="NI-NS", name="Nueva Segovia", type_="Department"),
        NISubdivision(code="NI-RI", name="Rivas", type_="Department"),
        NISubdivision(code="NI-SJ", name="Río San Juan", type_="Department"),
    ],
)
