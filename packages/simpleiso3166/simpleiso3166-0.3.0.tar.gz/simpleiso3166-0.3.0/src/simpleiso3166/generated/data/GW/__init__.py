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

GWSubdivisionCodeType = Literal[
    "GW-BA",  # Bafatá
    "GW-BL",  # Bolama / Bijagós
    "GW-BM",  # Biombo
    "GW-BS",  # Bissau
    "GW-CA",  # Cacheu
    "GW-GA",  # Gabú
    "GW-L",  # Leste
    "GW-N",  # Norte
    "GW-OI",  # Oio
    "GW-QU",  # Quinara
    "GW-S",  # Sul
    "GW-TO",  # Tombali
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class GWSubdivision(Subdivision):
    code: GWSubdivisionCodeType


GW: Final[Country] = Country(
    alpha2="GW",
    alpha3="GNB",
    name="Guinea-Bissau",
    common_name=None,
    official_name="Republic of Guinea-Bissau",
    subdivisions=[
        GWSubdivision(code="GW-BA", name="Bafatá", type_="Region"),
        GWSubdivision(code="GW-BL", name="Bolama / Bijagós", type_="Region"),
        GWSubdivision(code="GW-BM", name="Biombo", type_="Region"),
        GWSubdivision(code="GW-BS", name="Bissau", type_="Autonomous sector"),
        GWSubdivision(code="GW-CA", name="Cacheu", type_="Region"),
        GWSubdivision(code="GW-GA", name="Gabú", type_="Region"),
        GWSubdivision(code="GW-L", name="Leste", type_="Province"),
        GWSubdivision(code="GW-N", name="Norte", type_="Province"),
        GWSubdivision(code="GW-OI", name="Oio", type_="Region"),
        GWSubdivision(code="GW-QU", name="Quinara", type_="Region"),
        GWSubdivision(code="GW-S", name="Sul", type_="Province"),
        GWSubdivision(code="GW-TO", name="Tombali", type_="Region"),
    ],
)
