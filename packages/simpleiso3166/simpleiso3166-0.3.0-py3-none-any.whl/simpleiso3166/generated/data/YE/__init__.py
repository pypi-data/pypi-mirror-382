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

YESubdivisionCodeType = Literal[
    "YE-AB",  # Abyan
    "YE-AD",  # ‘Adan
    "YE-AM",  # ‘Amrān
    "YE-BA",  # Al Bayḑā’
    "YE-DA",  # Aḑ Ḑāli‘
    "YE-DH",  # Dhamār
    "YE-HD",  # Ḩaḑramawt
    "YE-HJ",  # Ḩajjah
    "YE-HU",  # Al Ḩudaydah
    "YE-IB",  # Ibb
    "YE-JA",  # Al Jawf
    "YE-LA",  # Laḩij
    "YE-MA",  # Ma’rib
    "YE-MR",  # Al Mahrah
    "YE-MW",  # Al Maḩwīt
    "YE-RA",  # Raymah
    "YE-SA",  # Amānat al ‘Āşimah [city]
    "YE-SD",  # Şāʻdah
    "YE-SH",  # Shabwah
    "YE-SN",  # Şanʻā’
    "YE-SU",  # Arkhabīl Suquţrá
    "YE-TA",  # Tāʻizz
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class YESubdivision(Subdivision):
    code: YESubdivisionCodeType


YE: Final[Country] = Country(
    alpha2="YE",
    alpha3="YEM",
    name="Yemen",
    common_name=None,
    official_name="Republic of Yemen",
    subdivisions=[
        YESubdivision(code="YE-AB", name="Abyan", type_="Governorate"),
        YESubdivision(code="YE-AD", name="‘Adan", type_="Governorate"),
        YESubdivision(code="YE-AM", name="‘Amrān", type_="Governorate"),
        YESubdivision(code="YE-BA", name="Al Bayḑā’", type_="Governorate"),
        YESubdivision(code="YE-DA", name="Aḑ Ḑāli‘", type_="Governorate"),
        YESubdivision(code="YE-DH", name="Dhamār", type_="Governorate"),
        YESubdivision(code="YE-HD", name="Ḩaḑramawt", type_="Governorate"),
        YESubdivision(code="YE-HJ", name="Ḩajjah", type_="Governorate"),
        YESubdivision(code="YE-HU", name="Al Ḩudaydah", type_="Governorate"),
        YESubdivision(code="YE-IB", name="Ibb", type_="Governorate"),
        YESubdivision(code="YE-JA", name="Al Jawf", type_="Governorate"),
        YESubdivision(code="YE-LA", name="Laḩij", type_="Governorate"),
        YESubdivision(code="YE-MA", name="Ma’rib", type_="Governorate"),
        YESubdivision(code="YE-MR", name="Al Mahrah", type_="Governorate"),
        YESubdivision(code="YE-MW", name="Al Maḩwīt", type_="Governorate"),
        YESubdivision(code="YE-RA", name="Raymah", type_="Governorate"),
        YESubdivision(code="YE-SA", name="Amānat al ‘Āşimah [city]", type_="Municipality"),
        YESubdivision(code="YE-SD", name="Şāʻdah", type_="Governorate"),
        YESubdivision(code="YE-SH", name="Shabwah", type_="Governorate"),
        YESubdivision(code="YE-SN", name="Şanʻā’", type_="Governorate"),
        YESubdivision(code="YE-SU", name="Arkhabīl Suquţrá", type_="Governorate"),
        YESubdivision(code="YE-TA", name="Tāʻizz", type_="Governorate"),
    ],
)
