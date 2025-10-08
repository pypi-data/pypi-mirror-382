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

TZSubdivisionCodeType = Literal[
    "TZ-01",  # Arusha
    "TZ-02",  # Dar es Salaam
    "TZ-03",  # Dodoma
    "TZ-04",  # Iringa
    "TZ-05",  # Kagera
    "TZ-06",  # Pemba North
    "TZ-07",  # Zanzibar North
    "TZ-08",  # Kigoma
    "TZ-09",  # Kilimanjaro
    "TZ-10",  # Pemba South
    "TZ-11",  # Zanzibar South
    "TZ-12",  # Lindi
    "TZ-13",  # Mara
    "TZ-14",  # Mbeya
    "TZ-15",  # Zanzibar West
    "TZ-16",  # Morogoro
    "TZ-17",  # Mtwara
    "TZ-18",  # Mwanza
    "TZ-19",  # Coast
    "TZ-20",  # Rukwa
    "TZ-21",  # Ruvuma
    "TZ-22",  # Shinyanga
    "TZ-23",  # Singida
    "TZ-24",  # Tabora
    "TZ-25",  # Tanga
    "TZ-26",  # Manyara
    "TZ-27",  # Geita
    "TZ-28",  # Katavi
    "TZ-29",  # Njombe
    "TZ-30",  # Simiyu
    "TZ-31",  # Songwe
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class TZSubdivision(Subdivision):
    code: TZSubdivisionCodeType


TZ: Final[Country] = Country(
    alpha2="TZ",
    alpha3="TZA",
    name="Tanzania, United Republic of",
    common_name="Tanzania",
    official_name="United Republic of Tanzania",
    subdivisions=[
        TZSubdivision(code="TZ-01", name="Arusha", type_="Region"),
        TZSubdivision(code="TZ-02", name="Dar es Salaam", type_="Region"),
        TZSubdivision(code="TZ-03", name="Dodoma", type_="Region"),
        TZSubdivision(code="TZ-04", name="Iringa", type_="Region"),
        TZSubdivision(code="TZ-05", name="Kagera", type_="Region"),
        TZSubdivision(code="TZ-06", name="Pemba North", type_="Region"),
        TZSubdivision(code="TZ-07", name="Zanzibar North", type_="Region"),
        TZSubdivision(code="TZ-08", name="Kigoma", type_="Region"),
        TZSubdivision(code="TZ-09", name="Kilimanjaro", type_="Region"),
        TZSubdivision(code="TZ-10", name="Pemba South", type_="Region"),
        TZSubdivision(code="TZ-11", name="Zanzibar South", type_="Region"),
        TZSubdivision(code="TZ-12", name="Lindi", type_="Region"),
        TZSubdivision(code="TZ-13", name="Mara", type_="Region"),
        TZSubdivision(code="TZ-14", name="Mbeya", type_="Region"),
        TZSubdivision(code="TZ-15", name="Zanzibar West", type_="Region"),
        TZSubdivision(code="TZ-16", name="Morogoro", type_="Region"),
        TZSubdivision(code="TZ-17", name="Mtwara", type_="Region"),
        TZSubdivision(code="TZ-18", name="Mwanza", type_="Region"),
        TZSubdivision(code="TZ-19", name="Coast", type_="Region"),
        TZSubdivision(code="TZ-20", name="Rukwa", type_="Region"),
        TZSubdivision(code="TZ-21", name="Ruvuma", type_="Region"),
        TZSubdivision(code="TZ-22", name="Shinyanga", type_="Region"),
        TZSubdivision(code="TZ-23", name="Singida", type_="Region"),
        TZSubdivision(code="TZ-24", name="Tabora", type_="Region"),
        TZSubdivision(code="TZ-25", name="Tanga", type_="Region"),
        TZSubdivision(code="TZ-26", name="Manyara", type_="Region"),
        TZSubdivision(code="TZ-27", name="Geita", type_="Region"),
        TZSubdivision(code="TZ-28", name="Katavi", type_="Region"),
        TZSubdivision(code="TZ-29", name="Njombe", type_="Region"),
        TZSubdivision(code="TZ-30", name="Simiyu", type_="Region"),
        TZSubdivision(code="TZ-31", name="Songwe", type_="Region"),
    ],
)
