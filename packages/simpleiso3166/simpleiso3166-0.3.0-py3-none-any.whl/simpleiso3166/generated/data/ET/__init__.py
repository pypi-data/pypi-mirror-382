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

ETSubdivisionCodeType = Literal[
    "ET-AA",  # Addis Ababa
    "ET-AF",  # Afar
    "ET-AM",  # Amara
    "ET-BE",  # Benshangul-Gumaz
    "ET-DD",  # Dire Dawa
    "ET-GA",  # Gambela Peoples
    "ET-HA",  # Harari People
    "ET-OR",  # Oromia
    "ET-SI",  # Sidama
    "ET-SN",  # Southern Nations, Nationalities and Peoples
    "ET-SO",  # Somali
    "ET-SW",  # Southwest Ethiopia Peoples
    "ET-TI",  # Tigrai
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class ETSubdivision(Subdivision):
    code: ETSubdivisionCodeType


ET: Final[Country] = Country(
    alpha2="ET",
    alpha3="ETH",
    name="Ethiopia",
    common_name=None,
    official_name="Federal Democratic Republic of Ethiopia",
    subdivisions=[
        ETSubdivision(code="ET-AA", name="Addis Ababa", type_="Administration"),
        ETSubdivision(code="ET-AF", name="Afar", type_="Regional state"),
        ETSubdivision(code="ET-AM", name="Amara", type_="Regional state"),
        ETSubdivision(code="ET-BE", name="Benshangul-Gumaz", type_="Regional state"),
        ETSubdivision(code="ET-DD", name="Dire Dawa", type_="Administration"),
        ETSubdivision(code="ET-GA", name="Gambela Peoples", type_="Regional state"),
        ETSubdivision(code="ET-HA", name="Harari People", type_="Regional state"),
        ETSubdivision(code="ET-OR", name="Oromia", type_="Regional state"),
        ETSubdivision(code="ET-SI", name="Sidama", type_="Regional state"),
        ETSubdivision(code="ET-SN", name="Southern Nations, Nationalities and Peoples", type_="Regional state"),
        ETSubdivision(code="ET-SO", name="Somali", type_="Regional state"),
        ETSubdivision(code="ET-SW", name="Southwest Ethiopia Peoples", type_="Regional state"),
        ETSubdivision(code="ET-TI", name="Tigrai", type_="Regional state"),
    ],
)
