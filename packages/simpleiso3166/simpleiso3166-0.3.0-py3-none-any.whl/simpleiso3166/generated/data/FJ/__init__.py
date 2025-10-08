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

FJSubdivisionCodeType = Literal[
    "FJ-01",  # Ba
    "FJ-02",  # Bua
    "FJ-03",  # Cakaudrove
    "FJ-04",  # Kadavu
    "FJ-05",  # Lau
    "FJ-06",  # Lomaiviti
    "FJ-07",  # Macuata
    "FJ-08",  # Nadroga and Navosa
    "FJ-09",  # Naitasiri
    "FJ-10",  # Namosi
    "FJ-11",  # Ra
    "FJ-12",  # Rewa
    "FJ-13",  # Serua
    "FJ-14",  # Tailevu
    "FJ-C",  # Central
    "FJ-E",  # Eastern
    "FJ-N",  # Northern
    "FJ-R",  # Rotuma
    "FJ-W",  # Western
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class FJSubdivision(Subdivision):
    code: FJSubdivisionCodeType


FJ: Final[Country] = Country(
    alpha2="FJ",
    alpha3="FJI",
    name="Fiji",
    common_name=None,
    official_name="Republic of Fiji",
    subdivisions=[
        FJSubdivision(code="FJ-01", name="Ba", type_="Province"),
        FJSubdivision(code="FJ-02", name="Bua", type_="Province"),
        FJSubdivision(code="FJ-03", name="Cakaudrove", type_="Province"),
        FJSubdivision(code="FJ-04", name="Kadavu", type_="Province"),
        FJSubdivision(code="FJ-05", name="Lau", type_="Province"),
        FJSubdivision(code="FJ-06", name="Lomaiviti", type_="Province"),
        FJSubdivision(code="FJ-07", name="Macuata", type_="Province"),
        FJSubdivision(code="FJ-08", name="Nadroga and Navosa", type_="Province"),
        FJSubdivision(code="FJ-09", name="Naitasiri", type_="Province"),
        FJSubdivision(code="FJ-10", name="Namosi", type_="Province"),
        FJSubdivision(code="FJ-11", name="Ra", type_="Province"),
        FJSubdivision(code="FJ-12", name="Rewa", type_="Province"),
        FJSubdivision(code="FJ-13", name="Serua", type_="Province"),
        FJSubdivision(code="FJ-14", name="Tailevu", type_="Province"),
        FJSubdivision(code="FJ-C", name="Central", type_="Division"),
        FJSubdivision(code="FJ-E", name="Eastern", type_="Division"),
        FJSubdivision(code="FJ-N", name="Northern", type_="Division"),
        FJSubdivision(code="FJ-R", name="Rotuma", type_="Dependency"),
        FJSubdivision(code="FJ-W", name="Western", type_="Division"),
    ],
)
