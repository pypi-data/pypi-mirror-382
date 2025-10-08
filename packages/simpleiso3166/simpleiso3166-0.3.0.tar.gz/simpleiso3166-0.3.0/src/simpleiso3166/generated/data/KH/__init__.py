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

KHSubdivisionCodeType = Literal[
    "KH-1",  # Banteay Mean Choăy
    "KH-10",  # Kracheh
    "KH-11",  # Mondol Kiri
    "KH-12",  # Phnom Penh
    "KH-13",  # Preah Vihear
    "KH-14",  # Prey Veaeng
    "KH-15",  # Pousaat
    "KH-16",  # Rotanak Kiri
    "KH-17",  # Siem Reab
    "KH-18",  # Preah Sihanouk
    "KH-19",  # Stoĕng Trêng
    "KH-2",  # Baat Dambang
    "KH-20",  # Svaay Rieng
    "KH-21",  # Taakaev
    "KH-22",  # Otdar Mean Chey
    "KH-23",  # Kaeb
    "KH-24",  # Pailin
    "KH-25",  # Tbong Khmum
    "KH-3",  # Kampong Chaam
    "KH-4",  # Kampong Chhnang
    "KH-5",  # Kampong Spueu
    "KH-6",  # Kampong Thum
    "KH-7",  # Kampot
    "KH-8",  # Kandaal
    "KH-9",  # Kaoh Kong
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class KHSubdivision(Subdivision):
    code: KHSubdivisionCodeType


KH: Final[Country] = Country(
    alpha2="KH",
    alpha3="KHM",
    name="Cambodia",
    common_name=None,
    official_name="Kingdom of Cambodia",
    subdivisions=[
        KHSubdivision(code="KH-1", name="Banteay Mean Choăy", type_="Province"),
        KHSubdivision(code="KH-10", name="Kracheh", type_="Province"),
        KHSubdivision(code="KH-11", name="Mondol Kiri", type_="Province"),
        KHSubdivision(code="KH-12", name="Phnom Penh", type_="Autonomous municipality"),
        KHSubdivision(code="KH-13", name="Preah Vihear", type_="Province"),
        KHSubdivision(code="KH-14", name="Prey Veaeng", type_="Province"),
        KHSubdivision(code="KH-15", name="Pousaat", type_="Province"),
        KHSubdivision(code="KH-16", name="Rotanak Kiri", type_="Province"),
        KHSubdivision(code="KH-17", name="Siem Reab", type_="Province"),
        KHSubdivision(code="KH-18", name="Preah Sihanouk", type_="Province"),
        KHSubdivision(code="KH-19", name="Stoĕng Trêng", type_="Province"),
        KHSubdivision(code="KH-2", name="Baat Dambang", type_="Province"),
        KHSubdivision(code="KH-20", name="Svaay Rieng", type_="Province"),
        KHSubdivision(code="KH-21", name="Taakaev", type_="Province"),
        KHSubdivision(code="KH-22", name="Otdar Mean Chey", type_="Province"),
        KHSubdivision(code="KH-23", name="Kaeb", type_="Province"),
        KHSubdivision(code="KH-24", name="Pailin", type_="Province"),
        KHSubdivision(code="KH-25", name="Tbong Khmum", type_="Province"),
        KHSubdivision(code="KH-3", name="Kampong Chaam", type_="Province"),
        KHSubdivision(code="KH-4", name="Kampong Chhnang", type_="Province"),
        KHSubdivision(code="KH-5", name="Kampong Spueu", type_="Province"),
        KHSubdivision(code="KH-6", name="Kampong Thum", type_="Province"),
        KHSubdivision(code="KH-7", name="Kampot", type_="Province"),
        KHSubdivision(code="KH-8", name="Kandaal", type_="Province"),
        KHSubdivision(code="KH-9", name="Kaoh Kong", type_="Province"),
    ],
)
