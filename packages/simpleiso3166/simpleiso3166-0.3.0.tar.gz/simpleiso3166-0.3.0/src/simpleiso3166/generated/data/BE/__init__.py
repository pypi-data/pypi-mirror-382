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

BESubdivisionCodeType = Literal[
    "BE-BRU",  # Bruxelles-Capitale, Région de
    "BE-VAN",  # Antwerpen
    "BE-VBR",  # Vlaams-Brabant
    "BE-VLG",  # Vlaams Gewest
    "BE-VLI",  # Limburg
    "BE-VOV",  # Oost-Vlaanderen
    "BE-VWV",  # West-Vlaanderen
    "BE-WAL",  # wallonne, Région
    "BE-WBR",  # Brabant wallon
    "BE-WHT",  # Hainaut
    "BE-WLG",  # Liège
    "BE-WLX",  # Luxembourg
    "BE-WNA",  # Namur
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BESubdivision(Subdivision):
    code: BESubdivisionCodeType


BE: Final[Country] = Country(
    alpha2="BE",
    alpha3="BEL",
    name="Belgium",
    common_name=None,
    official_name="Kingdom of Belgium",
    subdivisions=[
        BESubdivision(code="BE-BRU", name="Bruxelles-Capitale, Région de", type_="Region"),
        BESubdivision(code="BE-VAN", name="Antwerpen", type_="Province"),
        BESubdivision(code="BE-VBR", name="Vlaams-Brabant", type_="Province"),
        BESubdivision(code="BE-VLG", name="Vlaams Gewest", type_="Region"),
        BESubdivision(code="BE-VLI", name="Limburg", type_="Province"),
        BESubdivision(code="BE-VOV", name="Oost-Vlaanderen", type_="Province"),
        BESubdivision(code="BE-VWV", name="West-Vlaanderen", type_="Province"),
        BESubdivision(code="BE-WAL", name="wallonne, Région", type_="Region"),
        BESubdivision(code="BE-WBR", name="Brabant wallon", type_="Province"),
        BESubdivision(code="BE-WHT", name="Hainaut", type_="Province"),
        BESubdivision(code="BE-WLG", name="Liège", type_="Province"),
        BESubdivision(code="BE-WLX", name="Luxembourg", type_="Province"),
        BESubdivision(code="BE-WNA", name="Namur", type_="Province"),
    ],
)
