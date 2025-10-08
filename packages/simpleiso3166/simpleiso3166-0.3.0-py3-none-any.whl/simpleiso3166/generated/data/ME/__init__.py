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

MESubdivisionCodeType = Literal[
    "ME-01",  # Andrijevica
    "ME-02",  # Bar
    "ME-03",  # Berane
    "ME-04",  # Bijelo Polje
    "ME-05",  # Budva
    "ME-06",  # Cetinje
    "ME-07",  # Danilovgrad
    "ME-08",  # Herceg-Novi
    "ME-09",  # Kolašin
    "ME-10",  # Kotor
    "ME-11",  # Mojkovac
    "ME-12",  # Nikšić
    "ME-13",  # Plav
    "ME-14",  # Pljevlja
    "ME-15",  # Plužine
    "ME-16",  # Podgorica
    "ME-17",  # Rožaje
    "ME-18",  # Šavnik
    "ME-19",  # Tivat
    "ME-20",  # Ulcinj
    "ME-21",  # Žabljak
    "ME-22",  # Gusinje
    "ME-23",  # Petnjica
    "ME-24",  # Tuzi
    "ME-25",  # Zeta
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MESubdivision(Subdivision):
    code: MESubdivisionCodeType


ME: Final[Country] = Country(
    alpha2="ME",
    alpha3="MNE",
    name="Montenegro",
    common_name=None,
    official_name="Montenegro",
    subdivisions=[
        MESubdivision(code="ME-01", name="Andrijevica", type_="Municipality"),
        MESubdivision(code="ME-02", name="Bar", type_="Municipality"),
        MESubdivision(code="ME-03", name="Berane", type_="Municipality"),
        MESubdivision(code="ME-04", name="Bijelo Polje", type_="Municipality"),
        MESubdivision(code="ME-05", name="Budva", type_="Municipality"),
        MESubdivision(code="ME-06", name="Cetinje", type_="Municipality"),
        MESubdivision(code="ME-07", name="Danilovgrad", type_="Municipality"),
        MESubdivision(code="ME-08", name="Herceg-Novi", type_="Municipality"),
        MESubdivision(code="ME-09", name="Kolašin", type_="Municipality"),
        MESubdivision(code="ME-10", name="Kotor", type_="Municipality"),
        MESubdivision(code="ME-11", name="Mojkovac", type_="Municipality"),
        MESubdivision(code="ME-12", name="Nikšić", type_="Municipality"),
        MESubdivision(code="ME-13", name="Plav", type_="Municipality"),
        MESubdivision(code="ME-14", name="Pljevlja", type_="Municipality"),
        MESubdivision(code="ME-15", name="Plužine", type_="Municipality"),
        MESubdivision(code="ME-16", name="Podgorica", type_="Municipality"),
        MESubdivision(code="ME-17", name="Rožaje", type_="Municipality"),
        MESubdivision(code="ME-18", name="Šavnik", type_="Municipality"),
        MESubdivision(code="ME-19", name="Tivat", type_="Municipality"),
        MESubdivision(code="ME-20", name="Ulcinj", type_="Municipality"),
        MESubdivision(code="ME-21", name="Žabljak", type_="Municipality"),
        MESubdivision(code="ME-22", name="Gusinje", type_="Municipality"),
        MESubdivision(code="ME-23", name="Petnjica", type_="Municipality"),
        MESubdivision(code="ME-24", name="Tuzi", type_="Municipality"),
        MESubdivision(code="ME-25", name="Zeta", type_="Municipality"),
    ],
)
