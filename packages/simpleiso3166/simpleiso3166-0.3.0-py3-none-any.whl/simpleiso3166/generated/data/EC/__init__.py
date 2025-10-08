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

ECSubdivisionCodeType = Literal[
    "EC-A",  # Azuay
    "EC-B",  # Bolívar
    "EC-C",  # Carchi
    "EC-D",  # Orellana
    "EC-E",  # Esmeraldas
    "EC-F",  # Cañar
    "EC-G",  # Guayas
    "EC-H",  # Chimborazo
    "EC-I",  # Imbabura
    "EC-L",  # Loja
    "EC-M",  # Manabí
    "EC-N",  # Napo
    "EC-O",  # El Oro
    "EC-P",  # Pichincha
    "EC-R",  # Los Ríos
    "EC-S",  # Morona Santiago
    "EC-SD",  # Santo Domingo de los Tsáchilas
    "EC-SE",  # Santa Elena
    "EC-T",  # Tungurahua
    "EC-U",  # Sucumbíos
    "EC-W",  # Galápagos
    "EC-X",  # Cotopaxi
    "EC-Y",  # Pastaza
    "EC-Z",  # Zamora Chinchipe
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class ECSubdivision(Subdivision):
    code: ECSubdivisionCodeType


EC: Final[Country] = Country(
    alpha2="EC",
    alpha3="ECU",
    name="Ecuador",
    common_name=None,
    official_name="Republic of Ecuador",
    subdivisions=[
        ECSubdivision(code="EC-A", name="Azuay", type_="Province"),
        ECSubdivision(code="EC-B", name="Bolívar", type_="Province"),
        ECSubdivision(code="EC-C", name="Carchi", type_="Province"),
        ECSubdivision(code="EC-D", name="Orellana", type_="Province"),
        ECSubdivision(code="EC-E", name="Esmeraldas", type_="Province"),
        ECSubdivision(code="EC-F", name="Cañar", type_="Province"),
        ECSubdivision(code="EC-G", name="Guayas", type_="Province"),
        ECSubdivision(code="EC-H", name="Chimborazo", type_="Province"),
        ECSubdivision(code="EC-I", name="Imbabura", type_="Province"),
        ECSubdivision(code="EC-L", name="Loja", type_="Province"),
        ECSubdivision(code="EC-M", name="Manabí", type_="Province"),
        ECSubdivision(code="EC-N", name="Napo", type_="Province"),
        ECSubdivision(code="EC-O", name="El Oro", type_="Province"),
        ECSubdivision(code="EC-P", name="Pichincha", type_="Province"),
        ECSubdivision(code="EC-R", name="Los Ríos", type_="Province"),
        ECSubdivision(code="EC-S", name="Morona Santiago", type_="Province"),
        ECSubdivision(code="EC-SD", name="Santo Domingo de los Tsáchilas", type_="Province"),
        ECSubdivision(code="EC-SE", name="Santa Elena", type_="Province"),
        ECSubdivision(code="EC-T", name="Tungurahua", type_="Province"),
        ECSubdivision(code="EC-U", name="Sucumbíos", type_="Province"),
        ECSubdivision(code="EC-W", name="Galápagos", type_="Province"),
        ECSubdivision(code="EC-X", name="Cotopaxi", type_="Province"),
        ECSubdivision(code="EC-Y", name="Pastaza", type_="Province"),
        ECSubdivision(code="EC-Z", name="Zamora Chinchipe", type_="Province"),
    ],
)
