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

ALSubdivisionCodeType = Literal[
    "AL-01",  # Berat
    "AL-02",  # Durrës
    "AL-03",  # Elbasan
    "AL-04",  # Fier
    "AL-05",  # Gjirokastër
    "AL-06",  # Korçë
    "AL-07",  # Kukës
    "AL-08",  # Lezhë
    "AL-09",  # Dibër
    "AL-10",  # Shkodër
    "AL-11",  # Tiranë
    "AL-12",  # Vlorë
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class ALSubdivision(Subdivision):
    code: ALSubdivisionCodeType


AL: Final[Country] = Country(
    alpha2="AL",
    alpha3="ALB",
    name="Albania",
    common_name=None,
    official_name="Republic of Albania",
    subdivisions=[
        ALSubdivision(code="AL-01", name="Berat", type_="County"),
        ALSubdivision(code="AL-02", name="Durrës", type_="County"),
        ALSubdivision(code="AL-03", name="Elbasan", type_="County"),
        ALSubdivision(code="AL-04", name="Fier", type_="County"),
        ALSubdivision(code="AL-05", name="Gjirokastër", type_="County"),
        ALSubdivision(code="AL-06", name="Korçë", type_="County"),
        ALSubdivision(code="AL-07", name="Kukës", type_="County"),
        ALSubdivision(code="AL-08", name="Lezhë", type_="County"),
        ALSubdivision(code="AL-09", name="Dibër", type_="County"),
        ALSubdivision(code="AL-10", name="Shkodër", type_="County"),
        ALSubdivision(code="AL-11", name="Tiranë", type_="County"),
        ALSubdivision(code="AL-12", name="Vlorë", type_="County"),
    ],
)
