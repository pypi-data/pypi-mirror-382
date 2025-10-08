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

OMSubdivisionCodeType = Literal[
    "OM-BJ",  # Janūb al Bāţinah
    "OM-BS",  # Shamāl al Bāţinah
    "OM-BU",  # Al Buraymī
    "OM-DA",  # Ad Dākhilīyah
    "OM-MA",  # Masqaţ
    "OM-MU",  # Musandam
    "OM-SJ",  # Janūb ash Sharqīyah
    "OM-SS",  # Shamāl ash Sharqīyah
    "OM-WU",  # Al Wusţá
    "OM-ZA",  # Az̧ Z̧āhirah
    "OM-ZU",  # Z̧ufār
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class OMSubdivision(Subdivision):
    code: OMSubdivisionCodeType


OM: Final[Country] = Country(
    alpha2="OM",
    alpha3="OMN",
    name="Oman",
    common_name=None,
    official_name="Sultanate of Oman",
    subdivisions=[
        OMSubdivision(code="OM-BJ", name="Janūb al Bāţinah", type_="Governorate"),
        OMSubdivision(code="OM-BS", name="Shamāl al Bāţinah", type_="Governorate"),
        OMSubdivision(code="OM-BU", name="Al Buraymī", type_="Governorate"),
        OMSubdivision(code="OM-DA", name="Ad Dākhilīyah", type_="Governorate"),
        OMSubdivision(code="OM-MA", name="Masqaţ", type_="Governorate"),
        OMSubdivision(code="OM-MU", name="Musandam", type_="Governorate"),
        OMSubdivision(code="OM-SJ", name="Janūb ash Sharqīyah", type_="Governorate"),
        OMSubdivision(code="OM-SS", name="Shamāl ash Sharqīyah", type_="Governorate"),
        OMSubdivision(code="OM-WU", name="Al Wusţá", type_="Governorate"),
        OMSubdivision(code="OM-ZA", name="Az̧ Z̧āhirah", type_="Governorate"),
        OMSubdivision(code="OM-ZU", name="Z̧ufār", type_="Governorate"),
    ],
)
