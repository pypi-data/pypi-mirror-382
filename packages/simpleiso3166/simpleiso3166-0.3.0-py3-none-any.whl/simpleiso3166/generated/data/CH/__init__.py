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

CHSubdivisionCodeType = Literal[
    "CH-AG",  # Aargau
    "CH-AI",  # Appenzell Innerrhoden
    "CH-AR",  # Appenzell Ausserrhoden
    "CH-BE",  # Berne
    "CH-BL",  # Basel-Landschaft
    "CH-BS",  # Basel-Stadt
    "CH-FR",  # Fribourg
    "CH-GE",  # Genève
    "CH-GL",  # Glarus
    "CH-GR",  # Graubünden
    "CH-JU",  # Jura
    "CH-LU",  # Luzern
    "CH-NE",  # Neuchâtel
    "CH-NW",  # Nidwalden
    "CH-OW",  # Obwalden
    "CH-SG",  # Sankt Gallen
    "CH-SH",  # Schaffhausen
    "CH-SO",  # Solothurn
    "CH-SZ",  # Schwyz
    "CH-TG",  # Thurgau
    "CH-TI",  # Ticino
    "CH-UR",  # Uri
    "CH-VD",  # Vaud
    "CH-VS",  # Valais
    "CH-ZG",  # Zug
    "CH-ZH",  # Zürich
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class CHSubdivision(Subdivision):
    code: CHSubdivisionCodeType


CH: Final[Country] = Country(
    alpha2="CH",
    alpha3="CHE",
    name="Switzerland",
    common_name=None,
    official_name="Swiss Confederation",
    subdivisions=[
        CHSubdivision(code="CH-AG", name="Aargau", type_="Canton"),
        CHSubdivision(code="CH-AI", name="Appenzell Innerrhoden", type_="Canton"),
        CHSubdivision(code="CH-AR", name="Appenzell Ausserrhoden", type_="Canton"),
        CHSubdivision(code="CH-BE", name="Berne", type_="Canton"),
        CHSubdivision(code="CH-BL", name="Basel-Landschaft", type_="Canton"),
        CHSubdivision(code="CH-BS", name="Basel-Stadt", type_="Canton"),
        CHSubdivision(code="CH-FR", name="Fribourg", type_="Canton"),
        CHSubdivision(code="CH-GE", name="Genève", type_="Canton"),
        CHSubdivision(code="CH-GL", name="Glarus", type_="Canton"),
        CHSubdivision(code="CH-GR", name="Graubünden", type_="Canton"),
        CHSubdivision(code="CH-JU", name="Jura", type_="Canton"),
        CHSubdivision(code="CH-LU", name="Luzern", type_="Canton"),
        CHSubdivision(code="CH-NE", name="Neuchâtel", type_="Canton"),
        CHSubdivision(code="CH-NW", name="Nidwalden", type_="Canton"),
        CHSubdivision(code="CH-OW", name="Obwalden", type_="Canton"),
        CHSubdivision(code="CH-SG", name="Sankt Gallen", type_="Canton"),
        CHSubdivision(code="CH-SH", name="Schaffhausen", type_="Canton"),
        CHSubdivision(code="CH-SO", name="Solothurn", type_="Canton"),
        CHSubdivision(code="CH-SZ", name="Schwyz", type_="Canton"),
        CHSubdivision(code="CH-TG", name="Thurgau", type_="Canton"),
        CHSubdivision(code="CH-TI", name="Ticino", type_="Canton"),
        CHSubdivision(code="CH-UR", name="Uri", type_="Canton"),
        CHSubdivision(code="CH-VD", name="Vaud", type_="Canton"),
        CHSubdivision(code="CH-VS", name="Valais", type_="Canton"),
        CHSubdivision(code="CH-ZG", name="Zug", type_="Canton"),
        CHSubdivision(code="CH-ZH", name="Zürich", type_="Canton"),
    ],
)
