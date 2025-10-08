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

LASubdivisionCodeType = Literal[
    "LA-AT",  # Attapu
    "LA-BK",  # Bokèo
    "LA-BL",  # Bolikhamxai
    "LA-CH",  # Champasak
    "LA-HO",  # Houaphan
    "LA-KH",  # Khammouan
    "LA-LM",  # Louang Namtha
    "LA-LP",  # Louangphabang
    "LA-OU",  # Oudômxai
    "LA-PH",  # Phôngsali
    "LA-SL",  # Salavan
    "LA-SV",  # Savannakhét
    "LA-VI",  # Viangchan
    "LA-VT",  # Viangchan
    "LA-XA",  # Xaignabouli
    "LA-XE",  # Xékong
    "LA-XI",  # Xiangkhouang
    "LA-XS",  # Xaisômboun
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class LASubdivision(Subdivision):
    code: LASubdivisionCodeType


LA: Final[Country] = Country(
    alpha2="LA",
    alpha3="LAO",
    name="Lao People's Democratic Republic",
    common_name="Laos",
    official_name=None,
    subdivisions=[
        LASubdivision(code="LA-AT", name="Attapu", type_="Province"),
        LASubdivision(code="LA-BK", name="Bokèo", type_="Province"),
        LASubdivision(code="LA-BL", name="Bolikhamxai", type_="Province"),
        LASubdivision(code="LA-CH", name="Champasak", type_="Province"),
        LASubdivision(code="LA-HO", name="Houaphan", type_="Province"),
        LASubdivision(code="LA-KH", name="Khammouan", type_="Province"),
        LASubdivision(code="LA-LM", name="Louang Namtha", type_="Province"),
        LASubdivision(code="LA-LP", name="Louangphabang", type_="Province"),
        LASubdivision(code="LA-OU", name="Oudômxai", type_="Province"),
        LASubdivision(code="LA-PH", name="Phôngsali", type_="Province"),
        LASubdivision(code="LA-SL", name="Salavan", type_="Province"),
        LASubdivision(code="LA-SV", name="Savannakhét", type_="Province"),
        LASubdivision(code="LA-VI", name="Viangchan", type_="Province"),
        LASubdivision(code="LA-VT", name="Viangchan", type_="Prefecture"),
        LASubdivision(code="LA-XA", name="Xaignabouli", type_="Province"),
        LASubdivision(code="LA-XE", name="Xékong", type_="Province"),
        LASubdivision(code="LA-XI", name="Xiangkhouang", type_="Province"),
        LASubdivision(code="LA-XS", name="Xaisômboun", type_="Province"),
    ],
)
