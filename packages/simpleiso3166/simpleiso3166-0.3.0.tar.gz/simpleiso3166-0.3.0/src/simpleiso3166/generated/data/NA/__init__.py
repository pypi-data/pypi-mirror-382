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

NASubdivisionCodeType = Literal[
    "NA-CA",  # Zambezi
    "NA-ER",  # Erongo
    "NA-HA",  # Hardap
    "NA-KA",  # //Karas
    "NA-KE",  # Kavango East
    "NA-KH",  # Khomas
    "NA-KU",  # Kunene
    "NA-KW",  # Kavango West
    "NA-OD",  # Otjozondjupa
    "NA-OH",  # Omaheke
    "NA-ON",  # Oshana
    "NA-OS",  # Omusati
    "NA-OT",  # Oshikoto
    "NA-OW",  # Ohangwena
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class NASubdivision(Subdivision):
    code: NASubdivisionCodeType


NA: Final[Country] = Country(
    alpha2="NA",
    alpha3="NAM",
    name="Namibia",
    common_name=None,
    official_name="Republic of Namibia",
    subdivisions=[
        NASubdivision(code="NA-CA", name="Zambezi", type_="Region"),
        NASubdivision(code="NA-ER", name="Erongo", type_="Region"),
        NASubdivision(code="NA-HA", name="Hardap", type_="Region"),
        NASubdivision(code="NA-KA", name="//Karas", type_="Region"),
        NASubdivision(code="NA-KE", name="Kavango East", type_="Region"),
        NASubdivision(code="NA-KH", name="Khomas", type_="Region"),
        NASubdivision(code="NA-KU", name="Kunene", type_="Region"),
        NASubdivision(code="NA-KW", name="Kavango West", type_="Region"),
        NASubdivision(code="NA-OD", name="Otjozondjupa", type_="Region"),
        NASubdivision(code="NA-OH", name="Omaheke", type_="Region"),
        NASubdivision(code="NA-ON", name="Oshana", type_="Region"),
        NASubdivision(code="NA-OS", name="Omusati", type_="Region"),
        NASubdivision(code="NA-OT", name="Oshikoto", type_="Region"),
        NASubdivision(code="NA-OW", name="Ohangwena", type_="Region"),
    ],
)
