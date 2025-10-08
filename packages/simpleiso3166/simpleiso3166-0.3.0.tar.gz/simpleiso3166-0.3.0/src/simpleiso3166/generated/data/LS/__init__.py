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

LSSubdivisionCodeType = Literal[
    "LS-A",  # Maseru
    "LS-B",  # Botha-Bothe
    "LS-C",  # Leribe
    "LS-D",  # Berea
    "LS-E",  # Mafeteng
    "LS-F",  # Mohale's Hoek
    "LS-G",  # Quthing
    "LS-H",  # Qacha's Nek
    "LS-J",  # Mokhotlong
    "LS-K",  # Thaba-Tseka
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class LSSubdivision(Subdivision):
    code: LSSubdivisionCodeType


LS: Final[Country] = Country(
    alpha2="LS",
    alpha3="LSO",
    name="Lesotho",
    common_name=None,
    official_name="Kingdom of Lesotho",
    subdivisions=[
        LSSubdivision(code="LS-A", name="Maseru", type_="District"),
        LSSubdivision(code="LS-B", name="Botha-Bothe", type_="District"),
        LSSubdivision(code="LS-C", name="Leribe", type_="District"),
        LSSubdivision(code="LS-D", name="Berea", type_="District"),
        LSSubdivision(code="LS-E", name="Mafeteng", type_="District"),
        LSSubdivision(code="LS-F", name="Mohale's Hoek", type_="District"),
        LSSubdivision(code="LS-G", name="Quthing", type_="District"),
        LSSubdivision(code="LS-H", name="Qacha's Nek", type_="District"),
        LSSubdivision(code="LS-J", name="Mokhotlong", type_="District"),
        LSSubdivision(code="LS-K", name="Thaba-Tseka", type_="District"),
    ],
)
