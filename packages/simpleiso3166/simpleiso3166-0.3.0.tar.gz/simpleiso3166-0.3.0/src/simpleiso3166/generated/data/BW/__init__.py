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

BWSubdivisionCodeType = Literal[
    "BW-CE",  # Central
    "BW-CH",  # Chobe
    "BW-FR",  # Francistown
    "BW-GA",  # Gaborone
    "BW-GH",  # Ghanzi
    "BW-JW",  # Jwaneng
    "BW-KG",  # Kgalagadi
    "BW-KL",  # Kgatleng
    "BW-KW",  # Kweneng
    "BW-LO",  # Lobatse
    "BW-NE",  # North East
    "BW-NW",  # North West
    "BW-SE",  # South East
    "BW-SO",  # Southern
    "BW-SP",  # Selibe Phikwe
    "BW-ST",  # Sowa Town
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BWSubdivision(Subdivision):
    code: BWSubdivisionCodeType


BW: Final[Country] = Country(
    alpha2="BW",
    alpha3="BWA",
    name="Botswana",
    common_name=None,
    official_name="Republic of Botswana",
    subdivisions=[
        BWSubdivision(code="BW-CE", name="Central", type_="District"),
        BWSubdivision(code="BW-CH", name="Chobe", type_="District"),
        BWSubdivision(code="BW-FR", name="Francistown", type_="City"),
        BWSubdivision(code="BW-GA", name="Gaborone", type_="City"),
        BWSubdivision(code="BW-GH", name="Ghanzi", type_="District"),
        BWSubdivision(code="BW-JW", name="Jwaneng", type_="Town"),
        BWSubdivision(code="BW-KG", name="Kgalagadi", type_="District"),
        BWSubdivision(code="BW-KL", name="Kgatleng", type_="District"),
        BWSubdivision(code="BW-KW", name="Kweneng", type_="District"),
        BWSubdivision(code="BW-LO", name="Lobatse", type_="Town"),
        BWSubdivision(code="BW-NE", name="North East", type_="District"),
        BWSubdivision(code="BW-NW", name="North West", type_="District"),
        BWSubdivision(code="BW-SE", name="South East", type_="District"),
        BWSubdivision(code="BW-SO", name="Southern", type_="District"),
        BWSubdivision(code="BW-SP", name="Selibe Phikwe", type_="Town"),
        BWSubdivision(code="BW-ST", name="Sowa Town", type_="Town"),
    ],
)
