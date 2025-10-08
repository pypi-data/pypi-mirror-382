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

GRSubdivisionCodeType = Literal[
    "GR-69",  # Ágion Óros
    "GR-A",  # Anatolikí Makedonía kai Thráki
    "GR-B",  # Kentrikí Makedonía
    "GR-C",  # Dytikí Makedonía
    "GR-D",  # Ípeiros
    "GR-E",  # Thessalía
    "GR-F",  # Ionía Nísia
    "GR-G",  # Dytikí Elláda
    "GR-H",  # Stereá Elláda
    "GR-I",  # Attikí
    "GR-J",  # Pelopónnisos
    "GR-K",  # Vóreio Aigaío
    "GR-L",  # Nótio Aigaío
    "GR-M",  # Kríti
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class GRSubdivision(Subdivision):
    code: GRSubdivisionCodeType


GR: Final[Country] = Country(
    alpha2="GR",
    alpha3="GRC",
    name="Greece",
    common_name=None,
    official_name="Hellenic Republic",
    subdivisions=[
        GRSubdivision(code="GR-69", name="Ágion Óros", type_="Self-governed part"),
        GRSubdivision(code="GR-A", name="Anatolikí Makedonía kai Thráki", type_="Administrative region"),
        GRSubdivision(code="GR-B", name="Kentrikí Makedonía", type_="Administrative region"),
        GRSubdivision(code="GR-C", name="Dytikí Makedonía", type_="Administrative region"),
        GRSubdivision(code="GR-D", name="Ípeiros", type_="Administrative region"),
        GRSubdivision(code="GR-E", name="Thessalía", type_="Administrative region"),
        GRSubdivision(code="GR-F", name="Ionía Nísia", type_="Administrative region"),
        GRSubdivision(code="GR-G", name="Dytikí Elláda", type_="Administrative region"),
        GRSubdivision(code="GR-H", name="Stereá Elláda", type_="Administrative region"),
        GRSubdivision(code="GR-I", name="Attikí", type_="Administrative region"),
        GRSubdivision(code="GR-J", name="Pelopónnisos", type_="Administrative region"),
        GRSubdivision(code="GR-K", name="Vóreio Aigaío", type_="Administrative region"),
        GRSubdivision(code="GR-L", name="Nótio Aigaío", type_="Administrative region"),
        GRSubdivision(code="GR-M", name="Kríti", type_="Administrative region"),
    ],
)
