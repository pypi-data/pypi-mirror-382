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

NOSubdivisionCodeType = Literal[
    "NO-03",  # Oslo
    "NO-11",  # Rogaland
    "NO-15",  # Møre og Romsdal
    "NO-18",  # Nordland
    "NO-21",  # Svalbard (Arctic Region)
    "NO-22",  # Jan Mayen (Arctic Region)
    "NO-30",  # Viken
    "NO-34",  # Innlandet
    "NO-38",  # Vestfold og Telemark
    "NO-42",  # Agder
    "NO-46",  # Vestland
    "NO-50",  # Trööndelage
    "NO-54",  # Romssa ja Finnmárkku
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class NOSubdivision(Subdivision):
    code: NOSubdivisionCodeType


NO: Final[Country] = Country(
    alpha2="NO",
    alpha3="NOR",
    name="Norway",
    common_name=None,
    official_name="Kingdom of Norway",
    subdivisions=[
        NOSubdivision(code="NO-03", name="Oslo", type_="County"),
        NOSubdivision(code="NO-11", name="Rogaland", type_="County"),
        NOSubdivision(code="NO-15", name="Møre og Romsdal", type_="County"),
        NOSubdivision(code="NO-18", name="Nordland", type_="County"),
        NOSubdivision(code="NO-21", name="Svalbard (Arctic Region)", type_="Arctic region"),
        NOSubdivision(code="NO-22", name="Jan Mayen (Arctic Region)", type_="Arctic region"),
        NOSubdivision(code="NO-30", name="Viken", type_="County"),
        NOSubdivision(code="NO-34", name="Innlandet", type_="County"),
        NOSubdivision(code="NO-38", name="Vestfold og Telemark", type_="County"),
        NOSubdivision(code="NO-42", name="Agder", type_="County"),
        NOSubdivision(code="NO-46", name="Vestland", type_="County"),
        NOSubdivision(code="NO-50", name="Trööndelage", type_="County"),
        NOSubdivision(code="NO-54", name="Romssa ja Finnmárkku", type_="County"),
    ],
)
