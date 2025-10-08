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

EGSubdivisionCodeType = Literal[
    "EG-ALX",  # Al Iskandarīyah
    "EG-ASN",  # Aswān
    "EG-AST",  # Asyūţ
    "EG-BA",  # Al Baḩr al Aḩmar
    "EG-BH",  # Al Buḩayrah
    "EG-BNS",  # Banī Suwayf
    "EG-C",  # Al Qāhirah
    "EG-DK",  # Ad Daqahlīyah
    "EG-DT",  # Dumyāţ
    "EG-FYM",  # Al Fayyūm
    "EG-GH",  # Al Gharbīyah
    "EG-GZ",  # Al Jīzah
    "EG-IS",  # Al Ismā'īlīyah
    "EG-JS",  # Janūb Sīnā'
    "EG-KB",  # Al Qalyūbīyah
    "EG-KFS",  # Kafr ash Shaykh
    "EG-KN",  # Qinā
    "EG-LX",  # Al Uqşur
    "EG-MN",  # Al Minyā
    "EG-MNF",  # Al Minūfīyah
    "EG-MT",  # Maţrūḩ
    "EG-PTS",  # Būr Sa‘īd
    "EG-SHG",  # Sūhāj
    "EG-SHR",  # Ash Sharqīyah
    "EG-SIN",  # Shamāl Sīnā'
    "EG-SUZ",  # As Suways
    "EG-WAD",  # Al Wādī al Jadīd
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class EGSubdivision(Subdivision):
    code: EGSubdivisionCodeType


EG: Final[Country] = Country(
    alpha2="EG",
    alpha3="EGY",
    name="Egypt",
    common_name=None,
    official_name="Arab Republic of Egypt",
    subdivisions=[
        EGSubdivision(code="EG-ALX", name="Al Iskandarīyah", type_="Governorate"),
        EGSubdivision(code="EG-ASN", name="Aswān", type_="Governorate"),
        EGSubdivision(code="EG-AST", name="Asyūţ", type_="Governorate"),
        EGSubdivision(code="EG-BA", name="Al Baḩr al Aḩmar", type_="Governorate"),
        EGSubdivision(code="EG-BH", name="Al Buḩayrah", type_="Governorate"),
        EGSubdivision(code="EG-BNS", name="Banī Suwayf", type_="Governorate"),
        EGSubdivision(code="EG-C", name="Al Qāhirah", type_="Governorate"),
        EGSubdivision(code="EG-DK", name="Ad Daqahlīyah", type_="Governorate"),
        EGSubdivision(code="EG-DT", name="Dumyāţ", type_="Governorate"),
        EGSubdivision(code="EG-FYM", name="Al Fayyūm", type_="Governorate"),
        EGSubdivision(code="EG-GH", name="Al Gharbīyah", type_="Governorate"),
        EGSubdivision(code="EG-GZ", name="Al Jīzah", type_="Governorate"),
        EGSubdivision(code="EG-IS", name="Al Ismā'īlīyah", type_="Governorate"),
        EGSubdivision(code="EG-JS", name="Janūb Sīnā'", type_="Governorate"),
        EGSubdivision(code="EG-KB", name="Al Qalyūbīyah", type_="Governorate"),
        EGSubdivision(code="EG-KFS", name="Kafr ash Shaykh", type_="Governorate"),
        EGSubdivision(code="EG-KN", name="Qinā", type_="Governorate"),
        EGSubdivision(code="EG-LX", name="Al Uqşur", type_="Governorate"),
        EGSubdivision(code="EG-MN", name="Al Minyā", type_="Governorate"),
        EGSubdivision(code="EG-MNF", name="Al Minūfīyah", type_="Governorate"),
        EGSubdivision(code="EG-MT", name="Maţrūḩ", type_="Governorate"),
        EGSubdivision(code="EG-PTS", name="Būr Sa‘īd", type_="Governorate"),
        EGSubdivision(code="EG-SHG", name="Sūhāj", type_="Governorate"),
        EGSubdivision(code="EG-SHR", name="Ash Sharqīyah", type_="Governorate"),
        EGSubdivision(code="EG-SIN", name="Shamāl Sīnā'", type_="Governorate"),
        EGSubdivision(code="EG-SUZ", name="As Suways", type_="Governorate"),
        EGSubdivision(code="EG-WAD", name="Al Wādī al Jadīd", type_="Governorate"),
    ],
)
