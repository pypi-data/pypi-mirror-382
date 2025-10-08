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

BSSubdivisionCodeType = Literal[
    "BS-AK",  # Acklins
    "BS-BI",  # Bimini
    "BS-BP",  # Black Point
    "BS-BY",  # Berry Islands
    "BS-CE",  # Central Eleuthera
    "BS-CI",  # Cat Island
    "BS-CK",  # Crooked Island and Long Cay
    "BS-CO",  # Central Abaco
    "BS-CS",  # Central Andros
    "BS-EG",  # East Grand Bahama
    "BS-EX",  # Exuma
    "BS-FP",  # City of Freeport
    "BS-GC",  # Grand Cay
    "BS-HI",  # Harbour Island
    "BS-HT",  # Hope Town
    "BS-IN",  # Inagua
    "BS-LI",  # Long Island
    "BS-MC",  # Mangrove Cay
    "BS-MG",  # Mayaguana
    "BS-MI",  # Moore's Island
    "BS-NE",  # North Eleuthera
    "BS-NO",  # North Abaco
    "BS-NP",  # New Providence
    "BS-NS",  # North Andros
    "BS-RC",  # Rum Cay
    "BS-RI",  # Ragged Island
    "BS-SA",  # South Andros
    "BS-SE",  # South Eleuthera
    "BS-SO",  # South Abaco
    "BS-SS",  # San Salvador
    "BS-SW",  # Spanish Wells
    "BS-WG",  # West Grand Bahama
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BSSubdivision(Subdivision):
    code: BSSubdivisionCodeType


BS: Final[Country] = Country(
    alpha2="BS",
    alpha3="BHS",
    name="Bahamas",
    common_name=None,
    official_name="Commonwealth of the Bahamas",
    subdivisions=[
        BSSubdivision(code="BS-AK", name="Acklins", type_="District"),
        BSSubdivision(code="BS-BI", name="Bimini", type_="District"),
        BSSubdivision(code="BS-BP", name="Black Point", type_="District"),
        BSSubdivision(code="BS-BY", name="Berry Islands", type_="District"),
        BSSubdivision(code="BS-CE", name="Central Eleuthera", type_="District"),
        BSSubdivision(code="BS-CI", name="Cat Island", type_="District"),
        BSSubdivision(code="BS-CK", name="Crooked Island and Long Cay", type_="District"),
        BSSubdivision(code="BS-CO", name="Central Abaco", type_="District"),
        BSSubdivision(code="BS-CS", name="Central Andros", type_="District"),
        BSSubdivision(code="BS-EG", name="East Grand Bahama", type_="District"),
        BSSubdivision(code="BS-EX", name="Exuma", type_="District"),
        BSSubdivision(code="BS-FP", name="City of Freeport", type_="District"),
        BSSubdivision(code="BS-GC", name="Grand Cay", type_="District"),
        BSSubdivision(code="BS-HI", name="Harbour Island", type_="District"),
        BSSubdivision(code="BS-HT", name="Hope Town", type_="District"),
        BSSubdivision(code="BS-IN", name="Inagua", type_="District"),
        BSSubdivision(code="BS-LI", name="Long Island", type_="District"),
        BSSubdivision(code="BS-MC", name="Mangrove Cay", type_="District"),
        BSSubdivision(code="BS-MG", name="Mayaguana", type_="District"),
        BSSubdivision(code="BS-MI", name="Moore's Island", type_="District"),
        BSSubdivision(code="BS-NE", name="North Eleuthera", type_="District"),
        BSSubdivision(code="BS-NO", name="North Abaco", type_="District"),
        BSSubdivision(code="BS-NP", name="New Providence", type_="Island"),
        BSSubdivision(code="BS-NS", name="North Andros", type_="District"),
        BSSubdivision(code="BS-RC", name="Rum Cay", type_="District"),
        BSSubdivision(code="BS-RI", name="Ragged Island", type_="District"),
        BSSubdivision(code="BS-SA", name="South Andros", type_="District"),
        BSSubdivision(code="BS-SE", name="South Eleuthera", type_="District"),
        BSSubdivision(code="BS-SO", name="South Abaco", type_="District"),
        BSSubdivision(code="BS-SS", name="San Salvador", type_="District"),
        BSSubdivision(code="BS-SW", name="Spanish Wells", type_="District"),
        BSSubdivision(code="BS-WG", name="West Grand Bahama", type_="District"),
    ],
)
