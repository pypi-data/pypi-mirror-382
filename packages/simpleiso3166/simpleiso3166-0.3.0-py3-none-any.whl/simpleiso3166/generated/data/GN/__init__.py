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

GNSubdivisionCodeType = Literal[
    "GN-B",  # Boké
    "GN-BE",  # Beyla
    "GN-BF",  # Boffa
    "GN-BK",  # Boké
    "GN-C",  # Conakry
    "GN-CO",  # Coyah
    "GN-D",  # Kindia
    "GN-DB",  # Dabola
    "GN-DI",  # Dinguiraye
    "GN-DL",  # Dalaba
    "GN-DU",  # Dubréka
    "GN-F",  # Faranah
    "GN-FA",  # Faranah
    "GN-FO",  # Forécariah
    "GN-FR",  # Fria
    "GN-GA",  # Gaoual
    "GN-GU",  # Guékédou
    "GN-K",  # Kankan
    "GN-KA",  # Kankan
    "GN-KB",  # Koubia
    "GN-KD",  # Kindia
    "GN-KE",  # Kérouané
    "GN-KN",  # Koundara
    "GN-KO",  # Kouroussa
    "GN-KS",  # Kissidougou
    "GN-L",  # Labé
    "GN-LA",  # Labé
    "GN-LE",  # Lélouma
    "GN-LO",  # Lola
    "GN-M",  # Mamou
    "GN-MC",  # Macenta
    "GN-MD",  # Mandiana
    "GN-ML",  # Mali
    "GN-MM",  # Mamou
    "GN-N",  # Nzérékoré
    "GN-NZ",  # Nzérékoré
    "GN-PI",  # Pita
    "GN-SI",  # Siguiri
    "GN-TE",  # Télimélé
    "GN-TO",  # Tougué
    "GN-YO",  # Yomou
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class GNSubdivision(Subdivision):
    code: GNSubdivisionCodeType


GN: Final[Country] = Country(
    alpha2="GN",
    alpha3="GIN",
    name="Guinea",
    common_name=None,
    official_name="Republic of Guinea",
    subdivisions=[
        GNSubdivision(code="GN-B", name="Boké", type_="Administrative region"),
        GNSubdivision(code="GN-BE", name="Beyla", type_="Prefecture"),
        GNSubdivision(code="GN-BF", name="Boffa", type_="Prefecture"),
        GNSubdivision(code="GN-BK", name="Boké", type_="Prefecture"),
        GNSubdivision(code="GN-C", name="Conakry", type_="Governorate"),
        GNSubdivision(code="GN-CO", name="Coyah", type_="Prefecture"),
        GNSubdivision(code="GN-D", name="Kindia", type_="Administrative region"),
        GNSubdivision(code="GN-DB", name="Dabola", type_="Prefecture"),
        GNSubdivision(code="GN-DI", name="Dinguiraye", type_="Prefecture"),
        GNSubdivision(code="GN-DL", name="Dalaba", type_="Prefecture"),
        GNSubdivision(code="GN-DU", name="Dubréka", type_="Prefecture"),
        GNSubdivision(code="GN-F", name="Faranah", type_="Administrative region"),
        GNSubdivision(code="GN-FA", name="Faranah", type_="Prefecture"),
        GNSubdivision(code="GN-FO", name="Forécariah", type_="Prefecture"),
        GNSubdivision(code="GN-FR", name="Fria", type_="Prefecture"),
        GNSubdivision(code="GN-GA", name="Gaoual", type_="Prefecture"),
        GNSubdivision(code="GN-GU", name="Guékédou", type_="Prefecture"),
        GNSubdivision(code="GN-K", name="Kankan", type_="Administrative region"),
        GNSubdivision(code="GN-KA", name="Kankan", type_="Prefecture"),
        GNSubdivision(code="GN-KB", name="Koubia", type_="Prefecture"),
        GNSubdivision(code="GN-KD", name="Kindia", type_="Prefecture"),
        GNSubdivision(code="GN-KE", name="Kérouané", type_="Prefecture"),
        GNSubdivision(code="GN-KN", name="Koundara", type_="Prefecture"),
        GNSubdivision(code="GN-KO", name="Kouroussa", type_="Prefecture"),
        GNSubdivision(code="GN-KS", name="Kissidougou", type_="Prefecture"),
        GNSubdivision(code="GN-L", name="Labé", type_="Administrative region"),
        GNSubdivision(code="GN-LA", name="Labé", type_="Prefecture"),
        GNSubdivision(code="GN-LE", name="Lélouma", type_="Prefecture"),
        GNSubdivision(code="GN-LO", name="Lola", type_="Prefecture"),
        GNSubdivision(code="GN-M", name="Mamou", type_="Administrative region"),
        GNSubdivision(code="GN-MC", name="Macenta", type_="Prefecture"),
        GNSubdivision(code="GN-MD", name="Mandiana", type_="Prefecture"),
        GNSubdivision(code="GN-ML", name="Mali", type_="Prefecture"),
        GNSubdivision(code="GN-MM", name="Mamou", type_="Prefecture"),
        GNSubdivision(code="GN-N", name="Nzérékoré", type_="Administrative region"),
        GNSubdivision(code="GN-NZ", name="Nzérékoré", type_="Prefecture"),
        GNSubdivision(code="GN-PI", name="Pita", type_="Prefecture"),
        GNSubdivision(code="GN-SI", name="Siguiri", type_="Prefecture"),
        GNSubdivision(code="GN-TE", name="Télimélé", type_="Prefecture"),
        GNSubdivision(code="GN-TO", name="Tougué", type_="Prefecture"),
        GNSubdivision(code="GN-YO", name="Yomou", type_="Prefecture"),
    ],
)
