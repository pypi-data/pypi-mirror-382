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

ROSubdivisionCodeType = Literal[
    "RO-AB",  # Alba
    "RO-AG",  # Argeș
    "RO-AR",  # Arad
    "RO-B",  # București
    "RO-BC",  # Bacău
    "RO-BH",  # Bihor
    "RO-BN",  # Bistrița-Năsăud
    "RO-BR",  # Brăila
    "RO-BT",  # Botoșani
    "RO-BV",  # Brașov
    "RO-BZ",  # Buzău
    "RO-CJ",  # Cluj
    "RO-CL",  # Călărași
    "RO-CS",  # Caraș-Severin
    "RO-CT",  # Constanța
    "RO-CV",  # Covasna
    "RO-DB",  # Dâmbovița
    "RO-DJ",  # Dolj
    "RO-GJ",  # Gorj
    "RO-GL",  # Galați
    "RO-GR",  # Giurgiu
    "RO-HD",  # Hunedoara
    "RO-HR",  # Harghita
    "RO-IF",  # Ilfov
    "RO-IL",  # Ialomița
    "RO-IS",  # Iași
    "RO-MH",  # Mehedinți
    "RO-MM",  # Maramureș
    "RO-MS",  # Mureș
    "RO-NT",  # Neamț
    "RO-OT",  # Olt
    "RO-PH",  # Prahova
    "RO-SB",  # Sibiu
    "RO-SJ",  # Sălaj
    "RO-SM",  # Satu Mare
    "RO-SV",  # Suceava
    "RO-TL",  # Tulcea
    "RO-TM",  # Timiș
    "RO-TR",  # Teleorman
    "RO-VL",  # Vâlcea
    "RO-VN",  # Vrancea
    "RO-VS",  # Vaslui
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class ROSubdivision(Subdivision):
    code: ROSubdivisionCodeType


RO: Final[Country] = Country(
    alpha2="RO",
    alpha3="ROU",
    name="Romania",
    common_name=None,
    official_name=None,
    subdivisions=[
        ROSubdivision(code="RO-AB", name="Alba", type_="Department"),
        ROSubdivision(code="RO-AG", name="Argeș", type_="Department"),
        ROSubdivision(code="RO-AR", name="Arad", type_="Department"),
        ROSubdivision(code="RO-B", name="București", type_="Municipality"),
        ROSubdivision(code="RO-BC", name="Bacău", type_="Department"),
        ROSubdivision(code="RO-BH", name="Bihor", type_="Department"),
        ROSubdivision(code="RO-BN", name="Bistrița-Năsăud", type_="Department"),
        ROSubdivision(code="RO-BR", name="Brăila", type_="Department"),
        ROSubdivision(code="RO-BT", name="Botoșani", type_="Department"),
        ROSubdivision(code="RO-BV", name="Brașov", type_="Department"),
        ROSubdivision(code="RO-BZ", name="Buzău", type_="Department"),
        ROSubdivision(code="RO-CJ", name="Cluj", type_="Department"),
        ROSubdivision(code="RO-CL", name="Călărași", type_="Department"),
        ROSubdivision(code="RO-CS", name="Caraș-Severin", type_="Department"),
        ROSubdivision(code="RO-CT", name="Constanța", type_="Department"),
        ROSubdivision(code="RO-CV", name="Covasna", type_="Department"),
        ROSubdivision(code="RO-DB", name="Dâmbovița", type_="Department"),
        ROSubdivision(code="RO-DJ", name="Dolj", type_="Department"),
        ROSubdivision(code="RO-GJ", name="Gorj", type_="Department"),
        ROSubdivision(code="RO-GL", name="Galați", type_="Department"),
        ROSubdivision(code="RO-GR", name="Giurgiu", type_="Department"),
        ROSubdivision(code="RO-HD", name="Hunedoara", type_="Department"),
        ROSubdivision(code="RO-HR", name="Harghita", type_="Department"),
        ROSubdivision(code="RO-IF", name="Ilfov", type_="Department"),
        ROSubdivision(code="RO-IL", name="Ialomița", type_="Department"),
        ROSubdivision(code="RO-IS", name="Iași", type_="Department"),
        ROSubdivision(code="RO-MH", name="Mehedinți", type_="Department"),
        ROSubdivision(code="RO-MM", name="Maramureș", type_="Department"),
        ROSubdivision(code="RO-MS", name="Mureș", type_="Department"),
        ROSubdivision(code="RO-NT", name="Neamț", type_="Department"),
        ROSubdivision(code="RO-OT", name="Olt", type_="Department"),
        ROSubdivision(code="RO-PH", name="Prahova", type_="Department"),
        ROSubdivision(code="RO-SB", name="Sibiu", type_="Department"),
        ROSubdivision(code="RO-SJ", name="Sălaj", type_="Department"),
        ROSubdivision(code="RO-SM", name="Satu Mare", type_="Department"),
        ROSubdivision(code="RO-SV", name="Suceava", type_="Department"),
        ROSubdivision(code="RO-TL", name="Tulcea", type_="Department"),
        ROSubdivision(code="RO-TM", name="Timiș", type_="Department"),
        ROSubdivision(code="RO-TR", name="Teleorman", type_="Department"),
        ROSubdivision(code="RO-VL", name="Vâlcea", type_="Department"),
        ROSubdivision(code="RO-VN", name="Vrancea", type_="Department"),
        ROSubdivision(code="RO-VS", name="Vaslui", type_="Department"),
    ],
)
