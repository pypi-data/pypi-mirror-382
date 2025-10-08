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

VESubdivisionCodeType = Literal[
    "VE-A",  # Distrito Capital
    "VE-B",  # Anzoátegui
    "VE-C",  # Apure
    "VE-D",  # Aragua
    "VE-E",  # Barinas
    "VE-F",  # Bolívar
    "VE-G",  # Carabobo
    "VE-H",  # Cojedes
    "VE-I",  # Falcón
    "VE-J",  # Guárico
    "VE-K",  # Lara
    "VE-L",  # Mérida
    "VE-M",  # Miranda
    "VE-N",  # Monagas
    "VE-O",  # Nueva Esparta
    "VE-P",  # Portuguesa
    "VE-R",  # Sucre
    "VE-S",  # Táchira
    "VE-T",  # Trujillo
    "VE-U",  # Yaracuy
    "VE-V",  # Zulia
    "VE-W",  # Dependencias Federales
    "VE-X",  # La Guaira
    "VE-Y",  # Delta Amacuro
    "VE-Z",  # Amazonas
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class VESubdivision(Subdivision):
    code: VESubdivisionCodeType


VE: Final[Country] = Country(
    alpha2="VE",
    alpha3="VEN",
    name="Venezuela, Bolivarian Republic of",
    common_name="Venezuela",
    official_name="Bolivarian Republic of Venezuela",
    subdivisions=[
        VESubdivision(code="VE-A", name="Distrito Capital", type_="Capital district"),
        VESubdivision(code="VE-B", name="Anzoátegui", type_="State"),
        VESubdivision(code="VE-C", name="Apure", type_="State"),
        VESubdivision(code="VE-D", name="Aragua", type_="State"),
        VESubdivision(code="VE-E", name="Barinas", type_="State"),
        VESubdivision(code="VE-F", name="Bolívar", type_="State"),
        VESubdivision(code="VE-G", name="Carabobo", type_="State"),
        VESubdivision(code="VE-H", name="Cojedes", type_="State"),
        VESubdivision(code="VE-I", name="Falcón", type_="State"),
        VESubdivision(code="VE-J", name="Guárico", type_="State"),
        VESubdivision(code="VE-K", name="Lara", type_="State"),
        VESubdivision(code="VE-L", name="Mérida", type_="State"),
        VESubdivision(code="VE-M", name="Miranda", type_="State"),
        VESubdivision(code="VE-N", name="Monagas", type_="State"),
        VESubdivision(code="VE-O", name="Nueva Esparta", type_="State"),
        VESubdivision(code="VE-P", name="Portuguesa", type_="State"),
        VESubdivision(code="VE-R", name="Sucre", type_="State"),
        VESubdivision(code="VE-S", name="Táchira", type_="State"),
        VESubdivision(code="VE-T", name="Trujillo", type_="State"),
        VESubdivision(code="VE-U", name="Yaracuy", type_="State"),
        VESubdivision(code="VE-V", name="Zulia", type_="State"),
        VESubdivision(code="VE-W", name="Dependencias Federales", type_="Federal dependency"),
        VESubdivision(code="VE-X", name="La Guaira", type_="State"),
        VESubdivision(code="VE-Y", name="Delta Amacuro", type_="State"),
        VESubdivision(code="VE-Z", name="Amazonas", type_="State"),
    ],
)
