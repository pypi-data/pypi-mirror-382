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

IESubdivisionCodeType = Literal[
    "IE-C",  # Connaught
    "IE-CE",  # Clare
    "IE-CN",  # Cavan
    "IE-CO",  # Cork
    "IE-CW",  # Carlow
    "IE-D",  # Dublin
    "IE-DL",  # Donegal
    "IE-G",  # Galway
    "IE-KE",  # Kildare
    "IE-KK",  # Kilkenny
    "IE-KY",  # Kerry
    "IE-L",  # Leinster
    "IE-LD",  # Longford
    "IE-LH",  # Louth
    "IE-LK",  # Limerick
    "IE-LM",  # Leitrim
    "IE-LS",  # Laois
    "IE-M",  # Munster
    "IE-MH",  # Meath
    "IE-MN",  # Monaghan
    "IE-MO",  # Mayo
    "IE-OY",  # Offaly
    "IE-RN",  # Roscommon
    "IE-SO",  # Sligo
    "IE-TA",  # Tipperary
    "IE-U",  # Ulster
    "IE-WD",  # Waterford
    "IE-WH",  # Westmeath
    "IE-WW",  # Wicklow
    "IE-WX",  # Wexford
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class IESubdivision(Subdivision):
    code: IESubdivisionCodeType


IE: Final[Country] = Country(
    alpha2="IE",
    alpha3="IRL",
    name="Ireland",
    common_name=None,
    official_name=None,
    subdivisions=[
        IESubdivision(code="IE-C", name="Connaught", type_="Province"),
        IESubdivision(code="IE-CE", name="Clare", type_="County"),
        IESubdivision(code="IE-CN", name="Cavan", type_="County"),
        IESubdivision(code="IE-CO", name="Cork", type_="County"),
        IESubdivision(code="IE-CW", name="Carlow", type_="County"),
        IESubdivision(code="IE-D", name="Dublin", type_="County"),
        IESubdivision(code="IE-DL", name="Donegal", type_="County"),
        IESubdivision(code="IE-G", name="Galway", type_="County"),
        IESubdivision(code="IE-KE", name="Kildare", type_="County"),
        IESubdivision(code="IE-KK", name="Kilkenny", type_="County"),
        IESubdivision(code="IE-KY", name="Kerry", type_="County"),
        IESubdivision(code="IE-L", name="Leinster", type_="Province"),
        IESubdivision(code="IE-LD", name="Longford", type_="County"),
        IESubdivision(code="IE-LH", name="Louth", type_="County"),
        IESubdivision(code="IE-LK", name="Limerick", type_="County"),
        IESubdivision(code="IE-LM", name="Leitrim", type_="County"),
        IESubdivision(code="IE-LS", name="Laois", type_="County"),
        IESubdivision(code="IE-M", name="Munster", type_="Province"),
        IESubdivision(code="IE-MH", name="Meath", type_="County"),
        IESubdivision(code="IE-MN", name="Monaghan", type_="County"),
        IESubdivision(code="IE-MO", name="Mayo", type_="County"),
        IESubdivision(code="IE-OY", name="Offaly", type_="County"),
        IESubdivision(code="IE-RN", name="Roscommon", type_="County"),
        IESubdivision(code="IE-SO", name="Sligo", type_="County"),
        IESubdivision(code="IE-TA", name="Tipperary", type_="County"),
        IESubdivision(code="IE-U", name="Ulster", type_="Province"),
        IESubdivision(code="IE-WD", name="Waterford", type_="County"),
        IESubdivision(code="IE-WH", name="Westmeath", type_="County"),
        IESubdivision(code="IE-WW", name="Wicklow", type_="County"),
        IESubdivision(code="IE-WX", name="Wexford", type_="County"),
    ],
)
