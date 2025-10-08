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

SYSubdivisionCodeType = Literal[
    "SY-DI",  # Dimashq
    "SY-DR",  # Dar'ā
    "SY-DY",  # Dayr az Zawr
    "SY-HA",  # Al Ḩasakah
    "SY-HI",  # Ḩimş
    "SY-HL",  # Ḩalab
    "SY-HM",  # Ḩamāh
    "SY-ID",  # Idlib
    "SY-LA",  # Al Lādhiqīyah
    "SY-QU",  # Al Qunayţirah
    "SY-RA",  # Ar Raqqah
    "SY-RD",  # Rīf Dimashq
    "SY-SU",  # As Suwaydā'
    "SY-TA",  # Ţarţūs
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SYSubdivision(Subdivision):
    code: SYSubdivisionCodeType


SY: Final[Country] = Country(
    alpha2="SY",
    alpha3="SYR",
    name="Syrian Arab Republic",
    common_name="Syria",
    official_name=None,
    subdivisions=[
        SYSubdivision(code="SY-DI", name="Dimashq", type_="Province"),
        SYSubdivision(code="SY-DR", name="Dar'ā", type_="Province"),
        SYSubdivision(code="SY-DY", name="Dayr az Zawr", type_="Province"),
        SYSubdivision(code="SY-HA", name="Al Ḩasakah", type_="Province"),
        SYSubdivision(code="SY-HI", name="Ḩimş", type_="Province"),
        SYSubdivision(code="SY-HL", name="Ḩalab", type_="Province"),
        SYSubdivision(code="SY-HM", name="Ḩamāh", type_="Province"),
        SYSubdivision(code="SY-ID", name="Idlib", type_="Province"),
        SYSubdivision(code="SY-LA", name="Al Lādhiqīyah", type_="Province"),
        SYSubdivision(code="SY-QU", name="Al Qunayţirah", type_="Province"),
        SYSubdivision(code="SY-RA", name="Ar Raqqah", type_="Province"),
        SYSubdivision(code="SY-RD", name="Rīf Dimashq", type_="Province"),
        SYSubdivision(code="SY-SU", name="As Suwaydā'", type_="Province"),
        SYSubdivision(code="SY-TA", name="Ţarţūs", type_="Province"),
    ],
)
