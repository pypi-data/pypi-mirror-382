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

IQSubdivisionCodeType = Literal[
    "IQ-AN",  # Al Anbār
    "IQ-AR",  # Arbīl
    "IQ-BA",  # Al Başrah
    "IQ-BB",  # Bābil
    "IQ-BG",  # Baghdād
    "IQ-DA",  # Dahūk
    "IQ-DI",  # Diyālá
    "IQ-DQ",  # Dhī Qār
    "IQ-KA",  # Karbalā’
    "IQ-KI",  # Kirkūk
    "IQ-KR",  # Herêm-î Kurdistan
    "IQ-MA",  # Maysān
    "IQ-MU",  # Al Muthanná
    "IQ-NA",  # An Najaf
    "IQ-NI",  # Nīnawá
    "IQ-QA",  # Al Qādisīyah
    "IQ-SD",  # Şalāḩ ad Dīn
    "IQ-SU",  # As Sulaymānīyah
    "IQ-WA",  # Wāsiţ
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class IQSubdivision(Subdivision):
    code: IQSubdivisionCodeType


IQ: Final[Country] = Country(
    alpha2="IQ",
    alpha3="IRQ",
    name="Iraq",
    common_name=None,
    official_name="Republic of Iraq",
    subdivisions=[
        IQSubdivision(code="IQ-AN", name="Al Anbār", type_="Governorate"),
        IQSubdivision(code="IQ-AR", name="Arbīl", type_="Governorate"),
        IQSubdivision(code="IQ-BA", name="Al Başrah", type_="Governorate"),
        IQSubdivision(code="IQ-BB", name="Bābil", type_="Governorate"),
        IQSubdivision(code="IQ-BG", name="Baghdād", type_="Governorate"),
        IQSubdivision(code="IQ-DA", name="Dahūk", type_="Governorate"),
        IQSubdivision(code="IQ-DI", name="Diyālá", type_="Governorate"),
        IQSubdivision(code="IQ-DQ", name="Dhī Qār", type_="Governorate"),
        IQSubdivision(code="IQ-KA", name="Karbalā’", type_="Governorate"),
        IQSubdivision(code="IQ-KI", name="Kirkūk", type_="Governorate"),
        IQSubdivision(code="IQ-KR", name="Herêm-î Kurdistan", type_="Region"),
        IQSubdivision(code="IQ-MA", name="Maysān", type_="Governorate"),
        IQSubdivision(code="IQ-MU", name="Al Muthanná", type_="Governorate"),
        IQSubdivision(code="IQ-NA", name="An Najaf", type_="Governorate"),
        IQSubdivision(code="IQ-NI", name="Nīnawá", type_="Governorate"),
        IQSubdivision(code="IQ-QA", name="Al Qādisīyah", type_="Governorate"),
        IQSubdivision(code="IQ-SD", name="Şalāḩ ad Dīn", type_="Governorate"),
        IQSubdivision(code="IQ-SU", name="As Sulaymānīyah", type_="Governorate"),
        IQSubdivision(code="IQ-WA", name="Wāsiţ", type_="Governorate"),
    ],
)
