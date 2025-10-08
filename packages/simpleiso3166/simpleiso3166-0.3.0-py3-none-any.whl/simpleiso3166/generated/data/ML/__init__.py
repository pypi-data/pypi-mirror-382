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

MLSubdivisionCodeType = Literal[
    "ML-1",  # Kayes
    "ML-10",  # Taoudénit
    "ML-2",  # Koulikoro
    "ML-3",  # Sikasso
    "ML-4",  # Ségou
    "ML-5",  # Mopti
    "ML-6",  # Tombouctou
    "ML-7",  # Gao
    "ML-8",  # Kidal
    "ML-9",  # Ménaka
    "ML-BKO",  # Bamako
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MLSubdivision(Subdivision):
    code: MLSubdivisionCodeType


ML: Final[Country] = Country(
    alpha2="ML",
    alpha3="MLI",
    name="Mali",
    common_name=None,
    official_name="Republic of Mali",
    subdivisions=[
        MLSubdivision(code="ML-1", name="Kayes", type_="Region"),
        MLSubdivision(code="ML-10", name="Taoudénit", type_="Region"),
        MLSubdivision(code="ML-2", name="Koulikoro", type_="Region"),
        MLSubdivision(code="ML-3", name="Sikasso", type_="Region"),
        MLSubdivision(code="ML-4", name="Ségou", type_="Region"),
        MLSubdivision(code="ML-5", name="Mopti", type_="Region"),
        MLSubdivision(code="ML-6", name="Tombouctou", type_="Region"),
        MLSubdivision(code="ML-7", name="Gao", type_="Region"),
        MLSubdivision(code="ML-8", name="Kidal", type_="Region"),
        MLSubdivision(code="ML-9", name="Ménaka", type_="Region"),
        MLSubdivision(code="ML-BKO", name="Bamako", type_="District"),
    ],
)
