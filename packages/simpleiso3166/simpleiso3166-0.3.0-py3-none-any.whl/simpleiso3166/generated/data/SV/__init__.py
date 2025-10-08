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

SVSubdivisionCodeType = Literal[
    "SV-AH",  # Ahuachapán
    "SV-CA",  # Cabañas
    "SV-CH",  # Chalatenango
    "SV-CU",  # Cuscatlán
    "SV-LI",  # La Libertad
    "SV-MO",  # Morazán
    "SV-PA",  # La Paz
    "SV-SA",  # Santa Ana
    "SV-SM",  # San Miguel
    "SV-SO",  # Sonsonate
    "SV-SS",  # San Salvador
    "SV-SV",  # San Vicente
    "SV-UN",  # La Unión
    "SV-US",  # Usulután
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SVSubdivision(Subdivision):
    code: SVSubdivisionCodeType


SV: Final[Country] = Country(
    alpha2="SV",
    alpha3="SLV",
    name="El Salvador",
    common_name=None,
    official_name="Republic of El Salvador",
    subdivisions=[
        SVSubdivision(code="SV-AH", name="Ahuachapán", type_="Department"),
        SVSubdivision(code="SV-CA", name="Cabañas", type_="Department"),
        SVSubdivision(code="SV-CH", name="Chalatenango", type_="Department"),
        SVSubdivision(code="SV-CU", name="Cuscatlán", type_="Department"),
        SVSubdivision(code="SV-LI", name="La Libertad", type_="Department"),
        SVSubdivision(code="SV-MO", name="Morazán", type_="Department"),
        SVSubdivision(code="SV-PA", name="La Paz", type_="Department"),
        SVSubdivision(code="SV-SA", name="Santa Ana", type_="Department"),
        SVSubdivision(code="SV-SM", name="San Miguel", type_="Department"),
        SVSubdivision(code="SV-SO", name="Sonsonate", type_="Department"),
        SVSubdivision(code="SV-SS", name="San Salvador", type_="Department"),
        SVSubdivision(code="SV-SV", name="San Vicente", type_="Department"),
        SVSubdivision(code="SV-UN", name="La Unión", type_="Department"),
        SVSubdivision(code="SV-US", name="Usulután", type_="Department"),
    ],
)
