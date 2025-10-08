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

COSubdivisionCodeType = Literal[
    "CO-AMA",  # Amazonas
    "CO-ANT",  # Antioquia
    "CO-ARA",  # Arauca
    "CO-ATL",  # Atlántico
    "CO-BOL",  # Bolívar
    "CO-BOY",  # Boyacá
    "CO-CAL",  # Caldas
    "CO-CAQ",  # Caquetá
    "CO-CAS",  # Casanare
    "CO-CAU",  # Cauca
    "CO-CES",  # Cesar
    "CO-CHO",  # Chocó
    "CO-COR",  # Córdoba
    "CO-CUN",  # Cundinamarca
    "CO-DC",  # Distrito Capital de Bogotá
    "CO-GUA",  # Guainía
    "CO-GUV",  # Guaviare
    "CO-HUI",  # Huila
    "CO-LAG",  # La Guajira
    "CO-MAG",  # Magdalena
    "CO-MET",  # Meta
    "CO-NAR",  # Nariño
    "CO-NSA",  # Norte de Santander
    "CO-PUT",  # Putumayo
    "CO-QUI",  # Quindío
    "CO-RIS",  # Risaralda
    "CO-SAN",  # Santander
    "CO-SAP",  # San Andrés, Providencia y Santa Catalina
    "CO-SUC",  # Sucre
    "CO-TOL",  # Tolima
    "CO-VAC",  # Valle del Cauca
    "CO-VAU",  # Vaupés
    "CO-VID",  # Vichada
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class COSubdivision(Subdivision):
    code: COSubdivisionCodeType


CO: Final[Country] = Country(
    alpha2="CO",
    alpha3="COL",
    name="Colombia",
    common_name=None,
    official_name="Republic of Colombia",
    subdivisions=[
        COSubdivision(code="CO-AMA", name="Amazonas", type_="Department"),
        COSubdivision(code="CO-ANT", name="Antioquia", type_="Department"),
        COSubdivision(code="CO-ARA", name="Arauca", type_="Department"),
        COSubdivision(code="CO-ATL", name="Atlántico", type_="Department"),
        COSubdivision(code="CO-BOL", name="Bolívar", type_="Department"),
        COSubdivision(code="CO-BOY", name="Boyacá", type_="Department"),
        COSubdivision(code="CO-CAL", name="Caldas", type_="Department"),
        COSubdivision(code="CO-CAQ", name="Caquetá", type_="Department"),
        COSubdivision(code="CO-CAS", name="Casanare", type_="Department"),
        COSubdivision(code="CO-CAU", name="Cauca", type_="Department"),
        COSubdivision(code="CO-CES", name="Cesar", type_="Department"),
        COSubdivision(code="CO-CHO", name="Chocó", type_="Department"),
        COSubdivision(code="CO-COR", name="Córdoba", type_="Department"),
        COSubdivision(code="CO-CUN", name="Cundinamarca", type_="Department"),
        COSubdivision(code="CO-DC", name="Distrito Capital de Bogotá", type_="Capital district"),
        COSubdivision(code="CO-GUA", name="Guainía", type_="Department"),
        COSubdivision(code="CO-GUV", name="Guaviare", type_="Department"),
        COSubdivision(code="CO-HUI", name="Huila", type_="Department"),
        COSubdivision(code="CO-LAG", name="La Guajira", type_="Department"),
        COSubdivision(code="CO-MAG", name="Magdalena", type_="Department"),
        COSubdivision(code="CO-MET", name="Meta", type_="Department"),
        COSubdivision(code="CO-NAR", name="Nariño", type_="Department"),
        COSubdivision(code="CO-NSA", name="Norte de Santander", type_="Department"),
        COSubdivision(code="CO-PUT", name="Putumayo", type_="Department"),
        COSubdivision(code="CO-QUI", name="Quindío", type_="Department"),
        COSubdivision(code="CO-RIS", name="Risaralda", type_="Department"),
        COSubdivision(code="CO-SAN", name="Santander", type_="Department"),
        COSubdivision(code="CO-SAP", name="San Andrés, Providencia y Santa Catalina", type_="Department"),
        COSubdivision(code="CO-SUC", name="Sucre", type_="Department"),
        COSubdivision(code="CO-TOL", name="Tolima", type_="Department"),
        COSubdivision(code="CO-VAC", name="Valle del Cauca", type_="Department"),
        COSubdivision(code="CO-VAU", name="Vaupés", type_="Department"),
        COSubdivision(code="CO-VID", name="Vichada", type_="Department"),
    ],
)
