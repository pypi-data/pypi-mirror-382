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

CMSubdivisionCodeType = Literal[
    "CM-AD",  # Adamaoua
    "CM-CE",  # Centre
    "CM-EN",  # Far North
    "CM-ES",  # East
    "CM-LT",  # Littoral
    "CM-NO",  # North
    "CM-NW",  # North-West
    "CM-OU",  # West
    "CM-SU",  # South
    "CM-SW",  # South-West
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class CMSubdivision(Subdivision):
    code: CMSubdivisionCodeType


CM: Final[Country] = Country(
    alpha2="CM",
    alpha3="CMR",
    name="Cameroon",
    common_name=None,
    official_name="Republic of Cameroon",
    subdivisions=[
        CMSubdivision(code="CM-AD", name="Adamaoua", type_="Region"),
        CMSubdivision(code="CM-CE", name="Centre", type_="Region"),
        CMSubdivision(code="CM-EN", name="Far North", type_="Region"),
        CMSubdivision(code="CM-ES", name="East", type_="Region"),
        CMSubdivision(code="CM-LT", name="Littoral", type_="Region"),
        CMSubdivision(code="CM-NO", name="North", type_="Region"),
        CMSubdivision(code="CM-NW", name="North-West", type_="Region"),
        CMSubdivision(code="CM-OU", name="West", type_="Region"),
        CMSubdivision(code="CM-SU", name="South", type_="Region"),
        CMSubdivision(code="CM-SW", name="South-West", type_="Region"),
    ],
)
