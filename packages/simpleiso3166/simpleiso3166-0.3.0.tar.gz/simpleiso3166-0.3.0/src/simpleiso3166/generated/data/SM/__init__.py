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

SMSubdivisionCodeType = Literal[
    "SM-01",  # Acquaviva
    "SM-02",  # Chiesanuova
    "SM-03",  # Domagnano
    "SM-04",  # Faetano
    "SM-05",  # Fiorentino
    "SM-06",  # Borgo Maggiore
    "SM-07",  # Città di San Marino
    "SM-08",  # Montegiardino
    "SM-09",  # Serravalle
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SMSubdivision(Subdivision):
    code: SMSubdivisionCodeType


SM: Final[Country] = Country(
    alpha2="SM",
    alpha3="SMR",
    name="San Marino",
    common_name=None,
    official_name="Republic of San Marino",
    subdivisions=[
        SMSubdivision(code="SM-01", name="Acquaviva", type_="Municipality"),
        SMSubdivision(code="SM-02", name="Chiesanuova", type_="Municipality"),
        SMSubdivision(code="SM-03", name="Domagnano", type_="Municipality"),
        SMSubdivision(code="SM-04", name="Faetano", type_="Municipality"),
        SMSubdivision(code="SM-05", name="Fiorentino", type_="Municipality"),
        SMSubdivision(code="SM-06", name="Borgo Maggiore", type_="Municipality"),
        SMSubdivision(code="SM-07", name="Città di San Marino", type_="Municipality"),
        SMSubdivision(code="SM-08", name="Montegiardino", type_="Municipality"),
        SMSubdivision(code="SM-09", name="Serravalle", type_="Municipality"),
    ],
)
