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

CLSubdivisionCodeType = Literal[
    "CL-AI",  # Aisén del General Carlos Ibañez del Campo
    "CL-AN",  # Antofagasta
    "CL-AP",  # Arica y Parinacota
    "CL-AR",  # La Araucanía
    "CL-AT",  # Atacama
    "CL-BI",  # Biobío
    "CL-CO",  # Coquimbo
    "CL-LI",  # Libertador General Bernardo O'Higgins
    "CL-LL",  # Los Lagos
    "CL-LR",  # Los Ríos
    "CL-MA",  # Magallanes
    "CL-ML",  # Maule
    "CL-NB",  # Ñuble
    "CL-RM",  # Región Metropolitana de Santiago
    "CL-TA",  # Tarapacá
    "CL-VS",  # Valparaíso
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class CLSubdivision(Subdivision):
    code: CLSubdivisionCodeType


CL: Final[Country] = Country(
    alpha2="CL",
    alpha3="CHL",
    name="Chile",
    common_name=None,
    official_name="Republic of Chile",
    subdivisions=[
        CLSubdivision(code="CL-AI", name="Aisén del General Carlos Ibañez del Campo", type_="Region"),
        CLSubdivision(code="CL-AN", name="Antofagasta", type_="Region"),
        CLSubdivision(code="CL-AP", name="Arica y Parinacota", type_="Region"),
        CLSubdivision(code="CL-AR", name="La Araucanía", type_="Region"),
        CLSubdivision(code="CL-AT", name="Atacama", type_="Region"),
        CLSubdivision(code="CL-BI", name="Biobío", type_="Region"),
        CLSubdivision(code="CL-CO", name="Coquimbo", type_="Region"),
        CLSubdivision(code="CL-LI", name="Libertador General Bernardo O'Higgins", type_="Region"),
        CLSubdivision(code="CL-LL", name="Los Lagos", type_="Region"),
        CLSubdivision(code="CL-LR", name="Los Ríos", type_="Region"),
        CLSubdivision(code="CL-MA", name="Magallanes", type_="Region"),
        CLSubdivision(code="CL-ML", name="Maule", type_="Region"),
        CLSubdivision(code="CL-NB", name="Ñuble", type_="Region"),
        CLSubdivision(code="CL-RM", name="Región Metropolitana de Santiago", type_="Region"),
        CLSubdivision(code="CL-TA", name="Tarapacá", type_="Region"),
        CLSubdivision(code="CL-VS", name="Valparaíso", type_="Region"),
    ],
)
