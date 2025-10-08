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

HNSubdivisionCodeType = Literal[
    "HN-AT",  # Atlántida
    "HN-CH",  # Choluteca
    "HN-CL",  # Colón
    "HN-CM",  # Comayagua
    "HN-CP",  # Copán
    "HN-CR",  # Cortés
    "HN-EP",  # El Paraíso
    "HN-FM",  # Francisco Morazán
    "HN-GD",  # Gracias a Dios
    "HN-IB",  # Islas de la Bahía
    "HN-IN",  # Intibucá
    "HN-LE",  # Lempira
    "HN-LP",  # La Paz
    "HN-OC",  # Ocotepeque
    "HN-OL",  # Olancho
    "HN-SB",  # Santa Bárbara
    "HN-VA",  # Valle
    "HN-YO",  # Yoro
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class HNSubdivision(Subdivision):
    code: HNSubdivisionCodeType


HN: Final[Country] = Country(
    alpha2="HN",
    alpha3="HND",
    name="Honduras",
    common_name=None,
    official_name="Republic of Honduras",
    subdivisions=[
        HNSubdivision(code="HN-AT", name="Atlántida", type_="Department"),
        HNSubdivision(code="HN-CH", name="Choluteca", type_="Department"),
        HNSubdivision(code="HN-CL", name="Colón", type_="Department"),
        HNSubdivision(code="HN-CM", name="Comayagua", type_="Department"),
        HNSubdivision(code="HN-CP", name="Copán", type_="Department"),
        HNSubdivision(code="HN-CR", name="Cortés", type_="Department"),
        HNSubdivision(code="HN-EP", name="El Paraíso", type_="Department"),
        HNSubdivision(code="HN-FM", name="Francisco Morazán", type_="Department"),
        HNSubdivision(code="HN-GD", name="Gracias a Dios", type_="Department"),
        HNSubdivision(code="HN-IB", name="Islas de la Bahía", type_="Department"),
        HNSubdivision(code="HN-IN", name="Intibucá", type_="Department"),
        HNSubdivision(code="HN-LE", name="Lempira", type_="Department"),
        HNSubdivision(code="HN-LP", name="La Paz", type_="Department"),
        HNSubdivision(code="HN-OC", name="Ocotepeque", type_="Department"),
        HNSubdivision(code="HN-OL", name="Olancho", type_="Department"),
        HNSubdivision(code="HN-SB", name="Santa Bárbara", type_="Department"),
        HNSubdivision(code="HN-VA", name="Valle", type_="Department"),
        HNSubdivision(code="HN-YO", name="Yoro", type_="Department"),
    ],
)
