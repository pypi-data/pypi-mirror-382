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

MMSubdivisionCodeType = Literal[
    "MM-01",  # Sagaing
    "MM-02",  # Bago
    "MM-03",  # Magway
    "MM-04",  # Mandalay
    "MM-05",  # Tanintharyi
    "MM-06",  # Yangon
    "MM-07",  # Ayeyarwady
    "MM-11",  # Kachin
    "MM-12",  # Kayah
    "MM-13",  # Kayin
    "MM-14",  # Chin
    "MM-15",  # Mon
    "MM-16",  # Rakhine
    "MM-17",  # Shan
    "MM-18",  # Nay Pyi Taw
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MMSubdivision(Subdivision):
    code: MMSubdivisionCodeType


MM: Final[Country] = Country(
    alpha2="MM",
    alpha3="MMR",
    name="Myanmar",
    common_name=None,
    official_name="Republic of Myanmar",
    subdivisions=[
        MMSubdivision(code="MM-01", name="Sagaing", type_="Region"),
        MMSubdivision(code="MM-02", name="Bago", type_="Region"),
        MMSubdivision(code="MM-03", name="Magway", type_="Region"),
        MMSubdivision(code="MM-04", name="Mandalay", type_="Region"),
        MMSubdivision(code="MM-05", name="Tanintharyi", type_="Region"),
        MMSubdivision(code="MM-06", name="Yangon", type_="Region"),
        MMSubdivision(code="MM-07", name="Ayeyarwady", type_="Region"),
        MMSubdivision(code="MM-11", name="Kachin", type_="State"),
        MMSubdivision(code="MM-12", name="Kayah", type_="State"),
        MMSubdivision(code="MM-13", name="Kayin", type_="State"),
        MMSubdivision(code="MM-14", name="Chin", type_="State"),
        MMSubdivision(code="MM-15", name="Mon", type_="State"),
        MMSubdivision(code="MM-16", name="Rakhine", type_="State"),
        MMSubdivision(code="MM-17", name="Shan", type_="State"),
        MMSubdivision(code="MM-18", name="Nay Pyi Taw", type_="Union territory"),
    ],
)
