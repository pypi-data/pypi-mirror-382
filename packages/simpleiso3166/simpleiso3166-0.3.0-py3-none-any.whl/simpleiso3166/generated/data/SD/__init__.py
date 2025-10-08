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

SDSubdivisionCodeType = Literal[
    "SD-DC",  # Central Darfur
    "SD-DE",  # East Darfur
    "SD-DN",  # North Darfur
    "SD-DS",  # South Darfur
    "SD-DW",  # West Darfur
    "SD-GD",  # Gedaref
    "SD-GK",  # West Kordofan
    "SD-GZ",  # Gezira
    "SD-KA",  # Kassala
    "SD-KH",  # Khartoum
    "SD-KN",  # North Kordofan
    "SD-KS",  # South Kordofan
    "SD-NB",  # Blue Nile
    "SD-NO",  # Northern
    "SD-NR",  # River Nile
    "SD-NW",  # White Nile
    "SD-RS",  # Red Sea
    "SD-SI",  # Sennar
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SDSubdivision(Subdivision):
    code: SDSubdivisionCodeType


SD: Final[Country] = Country(
    alpha2="SD",
    alpha3="SDN",
    name="Sudan",
    common_name=None,
    official_name="Republic of the Sudan",
    subdivisions=[
        SDSubdivision(code="SD-DC", name="Central Darfur", type_="State"),
        SDSubdivision(code="SD-DE", name="East Darfur", type_="State"),
        SDSubdivision(code="SD-DN", name="North Darfur", type_="State"),
        SDSubdivision(code="SD-DS", name="South Darfur", type_="State"),
        SDSubdivision(code="SD-DW", name="West Darfur", type_="State"),
        SDSubdivision(code="SD-GD", name="Gedaref", type_="State"),
        SDSubdivision(code="SD-GK", name="West Kordofan", type_="State"),
        SDSubdivision(code="SD-GZ", name="Gezira", type_="State"),
        SDSubdivision(code="SD-KA", name="Kassala", type_="State"),
        SDSubdivision(code="SD-KH", name="Khartoum", type_="State"),
        SDSubdivision(code="SD-KN", name="North Kordofan", type_="State"),
        SDSubdivision(code="SD-KS", name="South Kordofan", type_="State"),
        SDSubdivision(code="SD-NB", name="Blue Nile", type_="State"),
        SDSubdivision(code="SD-NO", name="Northern", type_="State"),
        SDSubdivision(code="SD-NR", name="River Nile", type_="State"),
        SDSubdivision(code="SD-NW", name="White Nile", type_="State"),
        SDSubdivision(code="SD-RS", name="Red Sea", type_="State"),
        SDSubdivision(code="SD-SI", name="Sennar", type_="State"),
    ],
)
