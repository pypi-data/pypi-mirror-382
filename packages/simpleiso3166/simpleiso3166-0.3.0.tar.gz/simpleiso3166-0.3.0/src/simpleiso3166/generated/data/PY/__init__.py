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

PYSubdivisionCodeType = Literal[
    "PY-1",  # Concepción
    "PY-10",  # Alto Paraná
    "PY-11",  # Central
    "PY-12",  # Ñeembucú
    "PY-13",  # Amambay
    "PY-14",  # Canindeyú
    "PY-15",  # Presidente Hayes
    "PY-16",  # Alto Paraguay
    "PY-19",  # Boquerón
    "PY-2",  # San Pedro
    "PY-3",  # Cordillera
    "PY-4",  # Guairá
    "PY-5",  # Caaguazú
    "PY-6",  # Caazapá
    "PY-7",  # Itapúa
    "PY-8",  # Misiones
    "PY-9",  # Paraguarí
    "PY-ASU",  # Asunción
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class PYSubdivision(Subdivision):
    code: PYSubdivisionCodeType


PY: Final[Country] = Country(
    alpha2="PY",
    alpha3="PRY",
    name="Paraguay",
    common_name=None,
    official_name="Republic of Paraguay",
    subdivisions=[
        PYSubdivision(code="PY-1", name="Concepción", type_="Department"),
        PYSubdivision(code="PY-10", name="Alto Paraná", type_="Department"),
        PYSubdivision(code="PY-11", name="Central", type_="Department"),
        PYSubdivision(code="PY-12", name="Ñeembucú", type_="Department"),
        PYSubdivision(code="PY-13", name="Amambay", type_="Department"),
        PYSubdivision(code="PY-14", name="Canindeyú", type_="Department"),
        PYSubdivision(code="PY-15", name="Presidente Hayes", type_="Department"),
        PYSubdivision(code="PY-16", name="Alto Paraguay", type_="Department"),
        PYSubdivision(code="PY-19", name="Boquerón", type_="Department"),
        PYSubdivision(code="PY-2", name="San Pedro", type_="Department"),
        PYSubdivision(code="PY-3", name="Cordillera", type_="Department"),
        PYSubdivision(code="PY-4", name="Guairá", type_="Department"),
        PYSubdivision(code="PY-5", name="Caaguazú", type_="Department"),
        PYSubdivision(code="PY-6", name="Caazapá", type_="Department"),
        PYSubdivision(code="PY-7", name="Itapúa", type_="Department"),
        PYSubdivision(code="PY-8", name="Misiones", type_="Department"),
        PYSubdivision(code="PY-9", name="Paraguarí", type_="Department"),
        PYSubdivision(code="PY-ASU", name="Asunción", type_="Capital"),
    ],
)
