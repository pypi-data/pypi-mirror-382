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

LUSubdivisionCodeType = Literal[
    "LU-CA",  # Capellen
    "LU-CL",  # Clervaux
    "LU-DI",  # Diekirch
    "LU-EC",  # Echternach
    "LU-ES",  # Esch-sur-Alzette
    "LU-GR",  # Grevenmacher
    "LU-LU",  # Luxembourg
    "LU-ME",  # Mersch
    "LU-RD",  # Redange
    "LU-RM",  # Remich
    "LU-VD",  # Vianden
    "LU-WI",  # Wiltz
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class LUSubdivision(Subdivision):
    code: LUSubdivisionCodeType


LU: Final[Country] = Country(
    alpha2="LU",
    alpha3="LUX",
    name="Luxembourg",
    common_name=None,
    official_name="Grand Duchy of Luxembourg",
    subdivisions=[
        LUSubdivision(code="LU-CA", name="Capellen", type_="Canton"),
        LUSubdivision(code="LU-CL", name="Clervaux", type_="Canton"),
        LUSubdivision(code="LU-DI", name="Diekirch", type_="Canton"),
        LUSubdivision(code="LU-EC", name="Echternach", type_="Canton"),
        LUSubdivision(code="LU-ES", name="Esch-sur-Alzette", type_="Canton"),
        LUSubdivision(code="LU-GR", name="Grevenmacher", type_="Canton"),
        LUSubdivision(code="LU-LU", name="Luxembourg", type_="Canton"),
        LUSubdivision(code="LU-ME", name="Mersch", type_="Canton"),
        LUSubdivision(code="LU-RD", name="Redange", type_="Canton"),
        LUSubdivision(code="LU-RM", name="Remich", type_="Canton"),
        LUSubdivision(code="LU-VD", name="Vianden", type_="Canton"),
        LUSubdivision(code="LU-WI", name="Wiltz", type_="Canton"),
    ],
)
