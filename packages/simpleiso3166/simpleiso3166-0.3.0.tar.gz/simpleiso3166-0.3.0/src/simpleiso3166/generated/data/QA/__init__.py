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

QASubdivisionCodeType = Literal[
    "QA-DA",  # Ad Dawḩah
    "QA-KH",  # Al Khawr wa adh Dhakhīrah
    "QA-MS",  # Ash Shamāl
    "QA-RA",  # Ar Rayyān
    "QA-SH",  # Ash Shīḩānīyah
    "QA-US",  # Umm Şalāl
    "QA-WA",  # Al Wakrah
    "QA-ZA",  # Az̧ Z̧a‘āyin
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class QASubdivision(Subdivision):
    code: QASubdivisionCodeType


QA: Final[Country] = Country(
    alpha2="QA",
    alpha3="QAT",
    name="Qatar",
    common_name=None,
    official_name="State of Qatar",
    subdivisions=[
        QASubdivision(code="QA-DA", name="Ad Dawḩah", type_="Municipality"),
        QASubdivision(code="QA-KH", name="Al Khawr wa adh Dhakhīrah", type_="Municipality"),
        QASubdivision(code="QA-MS", name="Ash Shamāl", type_="Municipality"),
        QASubdivision(code="QA-RA", name="Ar Rayyān", type_="Municipality"),
        QASubdivision(code="QA-SH", name="Ash Shīḩānīyah", type_="Municipality"),
        QASubdivision(code="QA-US", name="Umm Şalāl", type_="Municipality"),
        QASubdivision(code="QA-WA", name="Al Wakrah", type_="Municipality"),
        QASubdivision(code="QA-ZA", name="Az̧ Z̧a‘āyin", type_="Municipality"),
    ],
)
