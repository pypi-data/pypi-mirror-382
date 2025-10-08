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

ARSubdivisionCodeType = Literal[
    "AR-A",  # Salta
    "AR-B",  # Buenos Aires
    "AR-C",  # Ciudad Autónoma de Buenos Aires
    "AR-D",  # San Luis
    "AR-E",  # Entre Ríos
    "AR-F",  # La Rioja
    "AR-G",  # Santiago del Estero
    "AR-H",  # Chaco
    "AR-J",  # San Juan
    "AR-K",  # Catamarca
    "AR-L",  # La Pampa
    "AR-M",  # Mendoza
    "AR-N",  # Misiones
    "AR-P",  # Formosa
    "AR-Q",  # Neuquén
    "AR-R",  # Río Negro
    "AR-S",  # Santa Fe
    "AR-T",  # Tucumán
    "AR-U",  # Chubut
    "AR-V",  # Tierra del Fuego
    "AR-W",  # Corrientes
    "AR-X",  # Córdoba
    "AR-Y",  # Jujuy
    "AR-Z",  # Santa Cruz
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class ARSubdivision(Subdivision):
    code: ARSubdivisionCodeType


AR: Final[Country] = Country(
    alpha2="AR",
    alpha3="ARG",
    name="Argentina",
    common_name=None,
    official_name="Argentine Republic",
    subdivisions=[
        ARSubdivision(code="AR-A", name="Salta", type_="Province"),
        ARSubdivision(code="AR-B", name="Buenos Aires", type_="Province"),
        ARSubdivision(code="AR-C", name="Ciudad Autónoma de Buenos Aires", type_="City"),
        ARSubdivision(code="AR-D", name="San Luis", type_="Province"),
        ARSubdivision(code="AR-E", name="Entre Ríos", type_="Province"),
        ARSubdivision(code="AR-F", name="La Rioja", type_="Province"),
        ARSubdivision(code="AR-G", name="Santiago del Estero", type_="Province"),
        ARSubdivision(code="AR-H", name="Chaco", type_="Province"),
        ARSubdivision(code="AR-J", name="San Juan", type_="Province"),
        ARSubdivision(code="AR-K", name="Catamarca", type_="Province"),
        ARSubdivision(code="AR-L", name="La Pampa", type_="Province"),
        ARSubdivision(code="AR-M", name="Mendoza", type_="Province"),
        ARSubdivision(code="AR-N", name="Misiones", type_="Province"),
        ARSubdivision(code="AR-P", name="Formosa", type_="Province"),
        ARSubdivision(code="AR-Q", name="Neuquén", type_="Province"),
        ARSubdivision(code="AR-R", name="Río Negro", type_="Province"),
        ARSubdivision(code="AR-S", name="Santa Fe", type_="Province"),
        ARSubdivision(code="AR-T", name="Tucumán", type_="Province"),
        ARSubdivision(code="AR-U", name="Chubut", type_="Province"),
        ARSubdivision(code="AR-V", name="Tierra del Fuego", type_="Province"),
        ARSubdivision(code="AR-W", name="Corrientes", type_="Province"),
        ARSubdivision(code="AR-X", name="Córdoba", type_="Province"),
        ARSubdivision(code="AR-Y", name="Jujuy", type_="Province"),
        ARSubdivision(code="AR-Z", name="Santa Cruz", type_="Province"),
    ],
)
