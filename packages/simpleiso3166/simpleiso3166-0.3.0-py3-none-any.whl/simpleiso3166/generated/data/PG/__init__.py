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

PGSubdivisionCodeType = Literal[
    "PG-CPK",  # Chimbu
    "PG-CPM",  # Central
    "PG-EBR",  # East New Britain
    "PG-EHG",  # Eastern Highlands
    "PG-EPW",  # Enga
    "PG-ESW",  # East Sepik
    "PG-GPK",  # Gulf
    "PG-HLA",  # Hela
    "PG-JWK",  # Jiwaka
    "PG-MBA",  # Milne Bay
    "PG-MPL",  # Morobe
    "PG-MPM",  # Madang
    "PG-MRL",  # Manus
    "PG-NCD",  # National Capital District (Port Moresby)
    "PG-NIK",  # New Ireland
    "PG-NPP",  # Northern
    "PG-NSB",  # Bougainville
    "PG-SAN",  # West Sepik
    "PG-SHM",  # Southern Highlands
    "PG-WBK",  # West New Britain
    "PG-WHM",  # Western Highlands
    "PG-WPD",  # Western
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class PGSubdivision(Subdivision):
    code: PGSubdivisionCodeType


PG: Final[Country] = Country(
    alpha2="PG",
    alpha3="PNG",
    name="Papua New Guinea",
    common_name=None,
    official_name="Independent State of Papua New Guinea",
    subdivisions=[
        PGSubdivision(code="PG-CPK", name="Chimbu", type_="Province"),
        PGSubdivision(code="PG-CPM", name="Central", type_="Province"),
        PGSubdivision(code="PG-EBR", name="East New Britain", type_="Province"),
        PGSubdivision(code="PG-EHG", name="Eastern Highlands", type_="Province"),
        PGSubdivision(code="PG-EPW", name="Enga", type_="Province"),
        PGSubdivision(code="PG-ESW", name="East Sepik", type_="Province"),
        PGSubdivision(code="PG-GPK", name="Gulf", type_="Province"),
        PGSubdivision(code="PG-HLA", name="Hela", type_="Province"),
        PGSubdivision(code="PG-JWK", name="Jiwaka", type_="Province"),
        PGSubdivision(code="PG-MBA", name="Milne Bay", type_="Province"),
        PGSubdivision(code="PG-MPL", name="Morobe", type_="Province"),
        PGSubdivision(code="PG-MPM", name="Madang", type_="Province"),
        PGSubdivision(code="PG-MRL", name="Manus", type_="Province"),
        PGSubdivision(code="PG-NCD", name="National Capital District (Port Moresby)", type_="District"),
        PGSubdivision(code="PG-NIK", name="New Ireland", type_="Province"),
        PGSubdivision(code="PG-NPP", name="Northern", type_="Province"),
        PGSubdivision(code="PG-NSB", name="Bougainville", type_="Autonomous region"),
        PGSubdivision(code="PG-SAN", name="West Sepik", type_="Province"),
        PGSubdivision(code="PG-SHM", name="Southern Highlands", type_="Province"),
        PGSubdivision(code="PG-WBK", name="West New Britain", type_="Province"),
        PGSubdivision(code="PG-WHM", name="Western Highlands", type_="Province"),
        PGSubdivision(code="PG-WPD", name="Western", type_="Province"),
    ],
)
