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

BTSubdivisionCodeType = Literal[
    "BT-11",  # Paro
    "BT-12",  # Chhukha
    "BT-13",  # Haa
    "BT-14",  # Samtse
    "BT-15",  # Thimphu
    "BT-21",  # Tsirang
    "BT-22",  # Dagana
    "BT-23",  # Punakha
    "BT-24",  # Wangdue Phodrang
    "BT-31",  # Sarpang
    "BT-32",  # Trongsa
    "BT-33",  # Bumthang
    "BT-34",  # Zhemgang
    "BT-41",  # Trashigang
    "BT-42",  # Monggar
    "BT-43",  # Pema Gatshel
    "BT-44",  # Lhuentse
    "BT-45",  # Samdrup Jongkhar
    "BT-GA",  # Gasa
    "BT-TY",  # Trashi Yangtse
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BTSubdivision(Subdivision):
    code: BTSubdivisionCodeType


BT: Final[Country] = Country(
    alpha2="BT",
    alpha3="BTN",
    name="Bhutan",
    common_name=None,
    official_name="Kingdom of Bhutan",
    subdivisions=[
        BTSubdivision(code="BT-11", name="Paro", type_="District"),
        BTSubdivision(code="BT-12", name="Chhukha", type_="District"),
        BTSubdivision(code="BT-13", name="Haa", type_="District"),
        BTSubdivision(code="BT-14", name="Samtse", type_="District"),
        BTSubdivision(code="BT-15", name="Thimphu", type_="District"),
        BTSubdivision(code="BT-21", name="Tsirang", type_="District"),
        BTSubdivision(code="BT-22", name="Dagana", type_="District"),
        BTSubdivision(code="BT-23", name="Punakha", type_="District"),
        BTSubdivision(code="BT-24", name="Wangdue Phodrang", type_="District"),
        BTSubdivision(code="BT-31", name="Sarpang", type_="District"),
        BTSubdivision(code="BT-32", name="Trongsa", type_="District"),
        BTSubdivision(code="BT-33", name="Bumthang", type_="District"),
        BTSubdivision(code="BT-34", name="Zhemgang", type_="District"),
        BTSubdivision(code="BT-41", name="Trashigang", type_="District"),
        BTSubdivision(code="BT-42", name="Monggar", type_="District"),
        BTSubdivision(code="BT-43", name="Pema Gatshel", type_="District"),
        BTSubdivision(code="BT-44", name="Lhuentse", type_="District"),
        BTSubdivision(code="BT-45", name="Samdrup Jongkhar", type_="District"),
        BTSubdivision(code="BT-GA", name="Gasa", type_="District"),
        BTSubdivision(code="BT-TY", name="Trashi Yangtse", type_="District"),
    ],
)
