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

MXSubdivisionCodeType = Literal[
    "MX-AGU",  # Aguascalientes
    "MX-BCN",  # Baja California
    "MX-BCS",  # Baja California Sur
    "MX-CAM",  # Campeche
    "MX-CHH",  # Chihuahua
    "MX-CHP",  # Chiapas
    "MX-CMX",  # Ciudad de México
    "MX-COA",  # Coahuila de Zaragoza
    "MX-COL",  # Colima
    "MX-DUR",  # Durango
    "MX-GRO",  # Guerrero
    "MX-GUA",  # Guanajuato
    "MX-HID",  # Hidalgo
    "MX-JAL",  # Jalisco
    "MX-MEX",  # México
    "MX-MIC",  # Michoacán de Ocampo
    "MX-MOR",  # Morelos
    "MX-NAY",  # Nayarit
    "MX-NLE",  # Nuevo León
    "MX-OAX",  # Oaxaca
    "MX-PUE",  # Puebla
    "MX-QUE",  # Querétaro
    "MX-ROO",  # Quintana Roo
    "MX-SIN",  # Sinaloa
    "MX-SLP",  # San Luis Potosí
    "MX-SON",  # Sonora
    "MX-TAB",  # Tabasco
    "MX-TAM",  # Tamaulipas
    "MX-TLA",  # Tlaxcala
    "MX-VER",  # Veracruz de Ignacio de la Llave
    "MX-YUC",  # Yucatán
    "MX-ZAC",  # Zacatecas
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MXSubdivision(Subdivision):
    code: MXSubdivisionCodeType


MX: Final[Country] = Country(
    alpha2="MX",
    alpha3="MEX",
    name="Mexico",
    common_name=None,
    official_name="United Mexican States",
    subdivisions=[
        MXSubdivision(code="MX-AGU", name="Aguascalientes", type_="State"),
        MXSubdivision(code="MX-BCN", name="Baja California", type_="State"),
        MXSubdivision(code="MX-BCS", name="Baja California Sur", type_="State"),
        MXSubdivision(code="MX-CAM", name="Campeche", type_="State"),
        MXSubdivision(code="MX-CHH", name="Chihuahua", type_="State"),
        MXSubdivision(code="MX-CHP", name="Chiapas", type_="State"),
        MXSubdivision(code="MX-CMX", name="Ciudad de México", type_="Federal entity"),
        MXSubdivision(code="MX-COA", name="Coahuila de Zaragoza", type_="State"),
        MXSubdivision(code="MX-COL", name="Colima", type_="State"),
        MXSubdivision(code="MX-DUR", name="Durango", type_="State"),
        MXSubdivision(code="MX-GRO", name="Guerrero", type_="State"),
        MXSubdivision(code="MX-GUA", name="Guanajuato", type_="State"),
        MXSubdivision(code="MX-HID", name="Hidalgo", type_="State"),
        MXSubdivision(code="MX-JAL", name="Jalisco", type_="State"),
        MXSubdivision(code="MX-MEX", name="México", type_="State"),
        MXSubdivision(code="MX-MIC", name="Michoacán de Ocampo", type_="State"),
        MXSubdivision(code="MX-MOR", name="Morelos", type_="State"),
        MXSubdivision(code="MX-NAY", name="Nayarit", type_="State"),
        MXSubdivision(code="MX-NLE", name="Nuevo León", type_="State"),
        MXSubdivision(code="MX-OAX", name="Oaxaca", type_="State"),
        MXSubdivision(code="MX-PUE", name="Puebla", type_="State"),
        MXSubdivision(code="MX-QUE", name="Querétaro", type_="State"),
        MXSubdivision(code="MX-ROO", name="Quintana Roo", type_="State"),
        MXSubdivision(code="MX-SIN", name="Sinaloa", type_="State"),
        MXSubdivision(code="MX-SLP", name="San Luis Potosí", type_="State"),
        MXSubdivision(code="MX-SON", name="Sonora", type_="State"),
        MXSubdivision(code="MX-TAB", name="Tabasco", type_="State"),
        MXSubdivision(code="MX-TAM", name="Tamaulipas", type_="State"),
        MXSubdivision(code="MX-TLA", name="Tlaxcala", type_="State"),
        MXSubdivision(code="MX-VER", name="Veracruz de Ignacio de la Llave", type_="State"),
        MXSubdivision(code="MX-YUC", name="Yucatán", type_="State"),
        MXSubdivision(code="MX-ZAC", name="Zacatecas", type_="State"),
    ],
)
