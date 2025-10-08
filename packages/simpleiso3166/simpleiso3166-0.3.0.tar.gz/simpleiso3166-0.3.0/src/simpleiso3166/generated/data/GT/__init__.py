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

GTSubdivisionCodeType = Literal[
    "GT-01",  # Guatemala
    "GT-02",  # El Progreso
    "GT-03",  # Sacatepéquez
    "GT-04",  # Chimaltenango
    "GT-05",  # Escuintla
    "GT-06",  # Santa Rosa
    "GT-07",  # Sololá
    "GT-08",  # Totonicapán
    "GT-09",  # Quetzaltenango
    "GT-10",  # Suchitepéquez
    "GT-11",  # Retalhuleu
    "GT-12",  # San Marcos
    "GT-13",  # Huehuetenango
    "GT-14",  # Quiché
    "GT-15",  # Baja Verapaz
    "GT-16",  # Alta Verapaz
    "GT-17",  # Petén
    "GT-18",  # Izabal
    "GT-19",  # Zacapa
    "GT-20",  # Chiquimula
    "GT-21",  # Jalapa
    "GT-22",  # Jutiapa
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class GTSubdivision(Subdivision):
    code: GTSubdivisionCodeType


GT: Final[Country] = Country(
    alpha2="GT",
    alpha3="GTM",
    name="Guatemala",
    common_name=None,
    official_name="Republic of Guatemala",
    subdivisions=[
        GTSubdivision(code="GT-01", name="Guatemala", type_="Department"),
        GTSubdivision(code="GT-02", name="El Progreso", type_="Department"),
        GTSubdivision(code="GT-03", name="Sacatepéquez", type_="Department"),
        GTSubdivision(code="GT-04", name="Chimaltenango", type_="Department"),
        GTSubdivision(code="GT-05", name="Escuintla", type_="Department"),
        GTSubdivision(code="GT-06", name="Santa Rosa", type_="Department"),
        GTSubdivision(code="GT-07", name="Sololá", type_="Department"),
        GTSubdivision(code="GT-08", name="Totonicapán", type_="Department"),
        GTSubdivision(code="GT-09", name="Quetzaltenango", type_="Department"),
        GTSubdivision(code="GT-10", name="Suchitepéquez", type_="Department"),
        GTSubdivision(code="GT-11", name="Retalhuleu", type_="Department"),
        GTSubdivision(code="GT-12", name="San Marcos", type_="Department"),
        GTSubdivision(code="GT-13", name="Huehuetenango", type_="Department"),
        GTSubdivision(code="GT-14", name="Quiché", type_="Department"),
        GTSubdivision(code="GT-15", name="Baja Verapaz", type_="Department"),
        GTSubdivision(code="GT-16", name="Alta Verapaz", type_="Department"),
        GTSubdivision(code="GT-17", name="Petén", type_="Department"),
        GTSubdivision(code="GT-18", name="Izabal", type_="Department"),
        GTSubdivision(code="GT-19", name="Zacapa", type_="Department"),
        GTSubdivision(code="GT-20", name="Chiquimula", type_="Department"),
        GTSubdivision(code="GT-21", name="Jalapa", type_="Department"),
        GTSubdivision(code="GT-22", name="Jutiapa", type_="Department"),
    ],
)
