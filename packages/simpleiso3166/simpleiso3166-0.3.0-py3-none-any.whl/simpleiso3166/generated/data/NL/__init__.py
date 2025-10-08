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

NLSubdivisionCodeType = Literal[
    "NL-AW",  # Aruba
    "NL-BQ1",  # Bonaire
    "NL-BQ2",  # Saba
    "NL-BQ3",  # Sint Eustatius
    "NL-CW",  # Curaçao
    "NL-DR",  # Drenthe
    "NL-FL",  # Flevoland
    "NL-FR",  # Fryslân
    "NL-GE",  # Gelderland
    "NL-GR",  # Groningen
    "NL-LI",  # Limburg
    "NL-NB",  # Noord-Brabant
    "NL-NH",  # Noord-Holland
    "NL-OV",  # Overijssel
    "NL-SX",  # Sint Maarten
    "NL-UT",  # Utrecht
    "NL-ZE",  # Zeeland
    "NL-ZH",  # Zuid-Holland
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class NLSubdivision(Subdivision):
    code: NLSubdivisionCodeType


NL: Final[Country] = Country(
    alpha2="NL",
    alpha3="NLD",
    name="Netherlands",
    common_name=None,
    official_name="Kingdom of the Netherlands",
    subdivisions=[
        NLSubdivision(code="NL-AW", name="Aruba", type_="Country"),
        NLSubdivision(code="NL-BQ1", name="Bonaire", type_="Special municipality"),
        NLSubdivision(code="NL-BQ2", name="Saba", type_="Special municipality"),
        NLSubdivision(code="NL-BQ3", name="Sint Eustatius", type_="Special municipality"),
        NLSubdivision(code="NL-CW", name="Curaçao", type_="Country"),
        NLSubdivision(code="NL-DR", name="Drenthe", type_="Province"),
        NLSubdivision(code="NL-FL", name="Flevoland", type_="Province"),
        NLSubdivision(code="NL-FR", name="Fryslân", type_="Province"),
        NLSubdivision(code="NL-GE", name="Gelderland", type_="Province"),
        NLSubdivision(code="NL-GR", name="Groningen", type_="Province"),
        NLSubdivision(code="NL-LI", name="Limburg", type_="Province"),
        NLSubdivision(code="NL-NB", name="Noord-Brabant", type_="Province"),
        NLSubdivision(code="NL-NH", name="Noord-Holland", type_="Province"),
        NLSubdivision(code="NL-OV", name="Overijssel", type_="Province"),
        NLSubdivision(code="NL-SX", name="Sint Maarten", type_="Country"),
        NLSubdivision(code="NL-UT", name="Utrecht", type_="Province"),
        NLSubdivision(code="NL-ZE", name="Zeeland", type_="Province"),
        NLSubdivision(code="NL-ZH", name="Zuid-Holland", type_="Province"),
    ],
)
