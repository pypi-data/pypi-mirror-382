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

CVSubdivisionCodeType = Literal[
    "CV-B",  # Ilhas de Barlavento
    "CV-BR",  # Brava
    "CV-BV",  # Boa Vista
    "CV-CA",  # Santa Catarina
    "CV-CF",  # Santa Catarina do Fogo
    "CV-CR",  # Santa Cruz
    "CV-MA",  # Maio
    "CV-MO",  # Mosteiros
    "CV-PA",  # Paul
    "CV-PN",  # Porto Novo
    "CV-PR",  # Praia
    "CV-RB",  # Ribeira Brava
    "CV-RG",  # Ribeira Grande
    "CV-RS",  # Ribeira Grande de Santiago
    "CV-S",  # Ilhas de Sotavento
    "CV-SD",  # São Domingos
    "CV-SF",  # São Filipe
    "CV-SL",  # Sal
    "CV-SM",  # São Miguel
    "CV-SO",  # São Lourenço dos Órgãos
    "CV-SS",  # São Salvador do Mundo
    "CV-SV",  # São Vicente
    "CV-TA",  # Tarrafal
    "CV-TS",  # Tarrafal de São Nicolau
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class CVSubdivision(Subdivision):
    code: CVSubdivisionCodeType


CV: Final[Country] = Country(
    alpha2="CV",
    alpha3="CPV",
    name="Cabo Verde",
    common_name=None,
    official_name="Republic of Cabo Verde",
    subdivisions=[
        CVSubdivision(code="CV-B", name="Ilhas de Barlavento", type_="Geographical region"),
        CVSubdivision(code="CV-BR", name="Brava", type_="Municipality"),
        CVSubdivision(code="CV-BV", name="Boa Vista", type_="Municipality"),
        CVSubdivision(code="CV-CA", name="Santa Catarina", type_="Municipality"),
        CVSubdivision(code="CV-CF", name="Santa Catarina do Fogo", type_="Municipality"),
        CVSubdivision(code="CV-CR", name="Santa Cruz", type_="Municipality"),
        CVSubdivision(code="CV-MA", name="Maio", type_="Municipality"),
        CVSubdivision(code="CV-MO", name="Mosteiros", type_="Municipality"),
        CVSubdivision(code="CV-PA", name="Paul", type_="Municipality"),
        CVSubdivision(code="CV-PN", name="Porto Novo", type_="Municipality"),
        CVSubdivision(code="CV-PR", name="Praia", type_="Municipality"),
        CVSubdivision(code="CV-RB", name="Ribeira Brava", type_="Municipality"),
        CVSubdivision(code="CV-RG", name="Ribeira Grande", type_="Municipality"),
        CVSubdivision(code="CV-RS", name="Ribeira Grande de Santiago", type_="Municipality"),
        CVSubdivision(code="CV-S", name="Ilhas de Sotavento", type_="Geographical region"),
        CVSubdivision(code="CV-SD", name="São Domingos", type_="Municipality"),
        CVSubdivision(code="CV-SF", name="São Filipe", type_="Municipality"),
        CVSubdivision(code="CV-SL", name="Sal", type_="Municipality"),
        CVSubdivision(code="CV-SM", name="São Miguel", type_="Municipality"),
        CVSubdivision(code="CV-SO", name="São Lourenço dos Órgãos", type_="Municipality"),
        CVSubdivision(code="CV-SS", name="São Salvador do Mundo", type_="Municipality"),
        CVSubdivision(code="CV-SV", name="São Vicente", type_="Municipality"),
        CVSubdivision(code="CV-TA", name="Tarrafal", type_="Municipality"),
        CVSubdivision(code="CV-TS", name="Tarrafal de São Nicolau", type_="Municipality"),
    ],
)
