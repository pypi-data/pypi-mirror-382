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

AESubdivisionCodeType = Literal[
    "AE-AJ",  # ‘Ajmān
    "AE-AZ",  # Abū Z̧aby
    "AE-DU",  # Dubayy
    "AE-FU",  # Al Fujayrah
    "AE-RK",  # Ra’s al Khaymah
    "AE-SH",  # Ash Shāriqah
    "AE-UQ",  # Umm al Qaywayn
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class AESubdivision(Subdivision):
    code: AESubdivisionCodeType


AE: Final[Country] = Country(
    alpha2="AE",
    alpha3="ARE",
    name="United Arab Emirates",
    common_name=None,
    official_name=None,
    subdivisions=[
        AESubdivision(code="AE-AJ", name="‘Ajmān", type_="Emirate"),
        AESubdivision(code="AE-AZ", name="Abū Z̧aby", type_="Emirate"),
        AESubdivision(code="AE-DU", name="Dubayy", type_="Emirate"),
        AESubdivision(code="AE-FU", name="Al Fujayrah", type_="Emirate"),
        AESubdivision(code="AE-RK", name="Ra’s al Khaymah", type_="Emirate"),
        AESubdivision(code="AE-SH", name="Ash Shāriqah", type_="Emirate"),
        AESubdivision(code="AE-UQ", name="Umm al Qaywayn", type_="Emirate"),
    ],
)
