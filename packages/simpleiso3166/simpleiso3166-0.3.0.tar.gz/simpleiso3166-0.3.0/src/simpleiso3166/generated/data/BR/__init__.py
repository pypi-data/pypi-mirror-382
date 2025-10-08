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

BRSubdivisionCodeType = Literal[
    "BR-AC",  # Acre
    "BR-AL",  # Alagoas
    "BR-AM",  # Amazonas
    "BR-AP",  # Amapá
    "BR-BA",  # Bahia
    "BR-CE",  # Ceará
    "BR-DF",  # Distrito Federal
    "BR-ES",  # Espírito Santo
    "BR-GO",  # Goiás
    "BR-MA",  # Maranhão
    "BR-MG",  # Minas Gerais
    "BR-MS",  # Mato Grosso do Sul
    "BR-MT",  # Mato Grosso
    "BR-PA",  # Pará
    "BR-PB",  # Paraíba
    "BR-PE",  # Pernambuco
    "BR-PI",  # Piauí
    "BR-PR",  # Paraná
    "BR-RJ",  # Rio de Janeiro
    "BR-RN",  # Rio Grande do Norte
    "BR-RO",  # Rondônia
    "BR-RR",  # Roraima
    "BR-RS",  # Rio Grande do Sul
    "BR-SC",  # Santa Catarina
    "BR-SE",  # Sergipe
    "BR-SP",  # São Paulo
    "BR-TO",  # Tocantins
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BRSubdivision(Subdivision):
    code: BRSubdivisionCodeType


BR: Final[Country] = Country(
    alpha2="BR",
    alpha3="BRA",
    name="Brazil",
    common_name=None,
    official_name="Federative Republic of Brazil",
    subdivisions=[
        BRSubdivision(code="BR-AC", name="Acre", type_="State"),
        BRSubdivision(code="BR-AL", name="Alagoas", type_="State"),
        BRSubdivision(code="BR-AM", name="Amazonas", type_="State"),
        BRSubdivision(code="BR-AP", name="Amapá", type_="State"),
        BRSubdivision(code="BR-BA", name="Bahia", type_="State"),
        BRSubdivision(code="BR-CE", name="Ceará", type_="State"),
        BRSubdivision(code="BR-DF", name="Distrito Federal", type_="Federal district"),
        BRSubdivision(code="BR-ES", name="Espírito Santo", type_="State"),
        BRSubdivision(code="BR-GO", name="Goiás", type_="State"),
        BRSubdivision(code="BR-MA", name="Maranhão", type_="State"),
        BRSubdivision(code="BR-MG", name="Minas Gerais", type_="State"),
        BRSubdivision(code="BR-MS", name="Mato Grosso do Sul", type_="State"),
        BRSubdivision(code="BR-MT", name="Mato Grosso", type_="State"),
        BRSubdivision(code="BR-PA", name="Pará", type_="State"),
        BRSubdivision(code="BR-PB", name="Paraíba", type_="State"),
        BRSubdivision(code="BR-PE", name="Pernambuco", type_="State"),
        BRSubdivision(code="BR-PI", name="Piauí", type_="State"),
        BRSubdivision(code="BR-PR", name="Paraná", type_="State"),
        BRSubdivision(code="BR-RJ", name="Rio de Janeiro", type_="State"),
        BRSubdivision(code="BR-RN", name="Rio Grande do Norte", type_="State"),
        BRSubdivision(code="BR-RO", name="Rondônia", type_="State"),
        BRSubdivision(code="BR-RR", name="Roraima", type_="State"),
        BRSubdivision(code="BR-RS", name="Rio Grande do Sul", type_="State"),
        BRSubdivision(code="BR-SC", name="Santa Catarina", type_="State"),
        BRSubdivision(code="BR-SE", name="Sergipe", type_="State"),
        BRSubdivision(code="BR-SP", name="São Paulo", type_="State"),
        BRSubdivision(code="BR-TO", name="Tocantins", type_="State"),
    ],
)
