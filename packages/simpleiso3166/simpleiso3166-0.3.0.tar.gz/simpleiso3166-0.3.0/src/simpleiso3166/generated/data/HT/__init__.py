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

HTSubdivisionCodeType = Literal[
    "HT-AR",  # Artibonite
    "HT-CE",  # Centre
    "HT-GA",  # Grande’Anse
    "HT-ND",  # Nord
    "HT-NE",  # Nord-Est
    "HT-NI",  # Nippes
    "HT-NO",  # Nord-Ouest
    "HT-OU",  # Ouest
    "HT-SD",  # Sud
    "HT-SE",  # Sud-Est
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class HTSubdivision(Subdivision):
    code: HTSubdivisionCodeType


HT: Final[Country] = Country(
    alpha2="HT",
    alpha3="HTI",
    name="Haiti",
    common_name=None,
    official_name="Republic of Haiti",
    subdivisions=[
        HTSubdivision(code="HT-AR", name="Artibonite", type_="Department"),
        HTSubdivision(code="HT-CE", name="Centre", type_="Department"),
        HTSubdivision(code="HT-GA", name="Grande’Anse", type_="Department"),
        HTSubdivision(code="HT-ND", name="Nord", type_="Department"),
        HTSubdivision(code="HT-NE", name="Nord-Est", type_="Department"),
        HTSubdivision(code="HT-NI", name="Nippes", type_="Department"),
        HTSubdivision(code="HT-NO", name="Nord-Ouest", type_="Department"),
        HTSubdivision(code="HT-OU", name="Ouest", type_="Department"),
        HTSubdivision(code="HT-SD", name="Sud", type_="Department"),
        HTSubdivision(code="HT-SE", name="Sud-Est", type_="Department"),
    ],
)
