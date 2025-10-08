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

KWSubdivisionCodeType = Literal[
    "KW-AH",  # Al Aḩmadī
    "KW-FA",  # Al Farwānīyah
    "KW-HA",  # Ḩawallī
    "KW-JA",  # Al Jahrā’
    "KW-KU",  # Al ‘Āşimah
    "KW-MU",  # Mubārak al Kabīr
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class KWSubdivision(Subdivision):
    code: KWSubdivisionCodeType


KW: Final[Country] = Country(
    alpha2="KW",
    alpha3="KWT",
    name="Kuwait",
    common_name=None,
    official_name="State of Kuwait",
    subdivisions=[
        KWSubdivision(code="KW-AH", name="Al Aḩmadī", type_="Governorate"),
        KWSubdivision(code="KW-FA", name="Al Farwānīyah", type_="Governorate"),
        KWSubdivision(code="KW-HA", name="Ḩawallī", type_="Governorate"),
        KWSubdivision(code="KW-JA", name="Al Jahrā’", type_="Governorate"),
        KWSubdivision(code="KW-KU", name="Al ‘Āşimah", type_="Governorate"),
        KWSubdivision(code="KW-MU", name="Mubārak al Kabīr", type_="Governorate"),
    ],
)
