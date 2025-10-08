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

JOSubdivisionCodeType = Literal[
    "JO-AJ",  # ‘Ajlūn
    "JO-AM",  # Al ‘A̅şimah
    "JO-AQ",  # Al ‘Aqabah
    "JO-AT",  # Aţ Ţafīlah
    "JO-AZ",  # Az Zarqā’
    "JO-BA",  # Al Balqā’
    "JO-IR",  # Irbid
    "JO-JA",  # Jarash
    "JO-KA",  # Al Karak
    "JO-MA",  # Al Mafraq
    "JO-MD",  # Mādabā
    "JO-MN",  # Ma‘ān
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class JOSubdivision(Subdivision):
    code: JOSubdivisionCodeType


JO: Final[Country] = Country(
    alpha2="JO",
    alpha3="JOR",
    name="Jordan",
    common_name=None,
    official_name="Hashemite Kingdom of Jordan",
    subdivisions=[
        JOSubdivision(code="JO-AJ", name="‘Ajlūn", type_="Governorate"),
        JOSubdivision(code="JO-AM", name="Al ‘A̅şimah", type_="Governorate"),
        JOSubdivision(code="JO-AQ", name="Al ‘Aqabah", type_="Governorate"),
        JOSubdivision(code="JO-AT", name="Aţ Ţafīlah", type_="Governorate"),
        JOSubdivision(code="JO-AZ", name="Az Zarqā’", type_="Governorate"),
        JOSubdivision(code="JO-BA", name="Al Balqā’", type_="Governorate"),
        JOSubdivision(code="JO-IR", name="Irbid", type_="Governorate"),
        JOSubdivision(code="JO-JA", name="Jarash", type_="Governorate"),
        JOSubdivision(code="JO-KA", name="Al Karak", type_="Governorate"),
        JOSubdivision(code="JO-MA", name="Al Mafraq", type_="Governorate"),
        JOSubdivision(code="JO-MD", name="Mādabā", type_="Governorate"),
        JOSubdivision(code="JO-MN", name="Ma‘ān", type_="Governorate"),
    ],
)
