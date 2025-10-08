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

CYSubdivisionCodeType = Literal[
    "CY-01",  # Lefkosia
    "CY-02",  # Lemesos
    "CY-03",  # Larnaka
    "CY-04",  # Ammochostos
    "CY-05",  # Baf
    "CY-06",  # Girne
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class CYSubdivision(Subdivision):
    code: CYSubdivisionCodeType


CY: Final[Country] = Country(
    alpha2="CY",
    alpha3="CYP",
    name="Cyprus",
    common_name=None,
    official_name="Republic of Cyprus",
    subdivisions=[
        CYSubdivision(code="CY-01", name="Lefkosia", type_="District"),
        CYSubdivision(code="CY-02", name="Lemesos", type_="District"),
        CYSubdivision(code="CY-03", name="Larnaka", type_="District"),
        CYSubdivision(code="CY-04", name="Ammochostos", type_="District"),
        CYSubdivision(code="CY-05", name="Baf", type_="District"),
        CYSubdivision(code="CY-06", name="Girne", type_="District"),
    ],
)
