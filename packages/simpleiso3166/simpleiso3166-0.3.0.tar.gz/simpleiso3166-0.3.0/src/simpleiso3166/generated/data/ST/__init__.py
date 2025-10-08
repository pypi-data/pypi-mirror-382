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

STSubdivisionCodeType = Literal[
    "ST-01",  # Água Grande
    "ST-02",  # Cantagalo
    "ST-03",  # Caué
    "ST-04",  # Lembá
    "ST-05",  # Lobata
    "ST-06",  # Mé-Zóchi
    "ST-P",  # Príncipe
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class STSubdivision(Subdivision):
    code: STSubdivisionCodeType


ST: Final[Country] = Country(
    alpha2="ST",
    alpha3="STP",
    name="Sao Tome and Principe",
    common_name=None,
    official_name="Democratic Republic of Sao Tome and Principe",
    subdivisions=[
        STSubdivision(code="ST-01", name="Água Grande", type_="District"),
        STSubdivision(code="ST-02", name="Cantagalo", type_="District"),
        STSubdivision(code="ST-03", name="Caué", type_="District"),
        STSubdivision(code="ST-04", name="Lembá", type_="District"),
        STSubdivision(code="ST-05", name="Lobata", type_="District"),
        STSubdivision(code="ST-06", name="Mé-Zóchi", type_="District"),
        STSubdivision(code="ST-P", name="Príncipe", type_="Autonomous region"),
    ],
)
