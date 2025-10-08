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

DOSubdivisionCodeType = Literal[
    "DO-01",  # Distrito Nacional (Santo Domingo)
    "DO-02",  # Azua
    "DO-03",  # Baoruco
    "DO-04",  # Barahona
    "DO-05",  # Dajabón
    "DO-06",  # Duarte
    "DO-07",  # Elías Piña
    "DO-08",  # El Seibo
    "DO-09",  # Espaillat
    "DO-10",  # Independencia
    "DO-11",  # La Altagracia
    "DO-12",  # La Romana
    "DO-13",  # La Vega
    "DO-14",  # María Trinidad Sánchez
    "DO-15",  # Monte Cristi
    "DO-16",  # Pedernales
    "DO-17",  # Peravia
    "DO-18",  # Puerto Plata
    "DO-19",  # Hermanas Mirabal
    "DO-20",  # Samaná
    "DO-21",  # San Cristóbal
    "DO-22",  # San Juan
    "DO-23",  # San Pedro de Macorís
    "DO-24",  # Sánchez Ramírez
    "DO-25",  # Santiago
    "DO-26",  # Santiago Rodríguez
    "DO-27",  # Valverde
    "DO-28",  # Monseñor Nouel
    "DO-29",  # Monte Plata
    "DO-30",  # Hato Mayor
    "DO-31",  # San José de Ocoa
    "DO-32",  # Santo Domingo
    "DO-33",  # Cibao Nordeste
    "DO-34",  # Cibao Noroeste
    "DO-35",  # Cibao Norte
    "DO-36",  # Cibao Sur
    "DO-37",  # El Valle
    "DO-38",  # Enriquillo
    "DO-39",  # Higuamo
    "DO-40",  # Ozama
    "DO-41",  # Valdesia
    "DO-42",  # Yuma
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class DOSubdivision(Subdivision):
    code: DOSubdivisionCodeType


DO: Final[Country] = Country(
    alpha2="DO",
    alpha3="DOM",
    name="Dominican Republic",
    common_name=None,
    official_name=None,
    subdivisions=[
        DOSubdivision(code="DO-01", name="Distrito Nacional (Santo Domingo)", type_="District"),
        DOSubdivision(code="DO-02", name="Azua", type_="Province"),
        DOSubdivision(code="DO-03", name="Baoruco", type_="Province"),
        DOSubdivision(code="DO-04", name="Barahona", type_="Province"),
        DOSubdivision(code="DO-05", name="Dajabón", type_="Province"),
        DOSubdivision(code="DO-06", name="Duarte", type_="Province"),
        DOSubdivision(code="DO-07", name="Elías Piña", type_="Province"),
        DOSubdivision(code="DO-08", name="El Seibo", type_="Province"),
        DOSubdivision(code="DO-09", name="Espaillat", type_="Province"),
        DOSubdivision(code="DO-10", name="Independencia", type_="Province"),
        DOSubdivision(code="DO-11", name="La Altagracia", type_="Province"),
        DOSubdivision(code="DO-12", name="La Romana", type_="Province"),
        DOSubdivision(code="DO-13", name="La Vega", type_="Province"),
        DOSubdivision(code="DO-14", name="María Trinidad Sánchez", type_="Province"),
        DOSubdivision(code="DO-15", name="Monte Cristi", type_="Province"),
        DOSubdivision(code="DO-16", name="Pedernales", type_="Province"),
        DOSubdivision(code="DO-17", name="Peravia", type_="Province"),
        DOSubdivision(code="DO-18", name="Puerto Plata", type_="Province"),
        DOSubdivision(code="DO-19", name="Hermanas Mirabal", type_="Province"),
        DOSubdivision(code="DO-20", name="Samaná", type_="Province"),
        DOSubdivision(code="DO-21", name="San Cristóbal", type_="Province"),
        DOSubdivision(code="DO-22", name="San Juan", type_="Province"),
        DOSubdivision(code="DO-23", name="San Pedro de Macorís", type_="Province"),
        DOSubdivision(code="DO-24", name="Sánchez Ramírez", type_="Province"),
        DOSubdivision(code="DO-25", name="Santiago", type_="Province"),
        DOSubdivision(code="DO-26", name="Santiago Rodríguez", type_="Province"),
        DOSubdivision(code="DO-27", name="Valverde", type_="Province"),
        DOSubdivision(code="DO-28", name="Monseñor Nouel", type_="Province"),
        DOSubdivision(code="DO-29", name="Monte Plata", type_="Province"),
        DOSubdivision(code="DO-30", name="Hato Mayor", type_="Province"),
        DOSubdivision(code="DO-31", name="San José de Ocoa", type_="Province"),
        DOSubdivision(code="DO-32", name="Santo Domingo", type_="Province"),
        DOSubdivision(code="DO-33", name="Cibao Nordeste", type_="Region"),
        DOSubdivision(code="DO-34", name="Cibao Noroeste", type_="Region"),
        DOSubdivision(code="DO-35", name="Cibao Norte", type_="Region"),
        DOSubdivision(code="DO-36", name="Cibao Sur", type_="Region"),
        DOSubdivision(code="DO-37", name="El Valle", type_="Region"),
        DOSubdivision(code="DO-38", name="Enriquillo", type_="Region"),
        DOSubdivision(code="DO-39", name="Higuamo", type_="Region"),
        DOSubdivision(code="DO-40", name="Ozama", type_="Region"),
        DOSubdivision(code="DO-41", name="Valdesia", type_="Region"),
        DOSubdivision(code="DO-42", name="Yuma", type_="Region"),
    ],
)
