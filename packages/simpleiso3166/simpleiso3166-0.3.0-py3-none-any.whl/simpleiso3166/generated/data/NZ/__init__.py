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

NZSubdivisionCodeType = Literal[
    "NZ-AUK",  # Auckland
    "NZ-BOP",  # Bay of Plenty
    "NZ-CAN",  # Canterbury
    "NZ-CIT",  # Chatham Islands Territory
    "NZ-GIS",  # Gisborne
    "NZ-HKB",  # Hawke's Bay
    "NZ-MBH",  # Marlborough
    "NZ-MWT",  # Manawatū-Whanganui
    "NZ-NSN",  # Nelson
    "NZ-NTL",  # Northland
    "NZ-OTA",  # Otago
    "NZ-STL",  # Southland
    "NZ-TAS",  # Tasman
    "NZ-TKI",  # Taranaki
    "NZ-WGN",  # Greater Wellington
    "NZ-WKO",  # Waikato
    "NZ-WTC",  # West Coast
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class NZSubdivision(Subdivision):
    code: NZSubdivisionCodeType


NZ: Final[Country] = Country(
    alpha2="NZ",
    alpha3="NZL",
    name="New Zealand",
    common_name=None,
    official_name=None,
    subdivisions=[
        NZSubdivision(code="NZ-AUK", name="Auckland", type_="Region"),
        NZSubdivision(code="NZ-BOP", name="Bay of Plenty", type_="Region"),
        NZSubdivision(code="NZ-CAN", name="Canterbury", type_="Region"),
        NZSubdivision(code="NZ-CIT", name="Chatham Islands Territory", type_="Special island authority"),
        NZSubdivision(code="NZ-GIS", name="Gisborne", type_="Region"),
        NZSubdivision(code="NZ-HKB", name="Hawke's Bay", type_="Region"),
        NZSubdivision(code="NZ-MBH", name="Marlborough", type_="Region"),
        NZSubdivision(code="NZ-MWT", name="Manawatū-Whanganui", type_="Region"),
        NZSubdivision(code="NZ-NSN", name="Nelson", type_="Region"),
        NZSubdivision(code="NZ-NTL", name="Northland", type_="Region"),
        NZSubdivision(code="NZ-OTA", name="Otago", type_="Region"),
        NZSubdivision(code="NZ-STL", name="Southland", type_="Region"),
        NZSubdivision(code="NZ-TAS", name="Tasman", type_="Region"),
        NZSubdivision(code="NZ-TKI", name="Taranaki", type_="Region"),
        NZSubdivision(code="NZ-WGN", name="Greater Wellington", type_="Region"),
        NZSubdivision(code="NZ-WKO", name="Waikato", type_="Region"),
        NZSubdivision(code="NZ-WTC", name="West Coast", type_="Region"),
    ],
)
