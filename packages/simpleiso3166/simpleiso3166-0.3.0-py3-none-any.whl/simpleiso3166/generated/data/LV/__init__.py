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

LVSubdivisionCodeType = Literal[
    "LV-002",  # Aizkraukles novads
    "LV-007",  # Alūksnes novads
    "LV-011",  # Ādažu novads
    "LV-015",  # Balvu novads
    "LV-016",  # Bauskas novads
    "LV-022",  # Cēsu novads
    "LV-026",  # Dobeles novads
    "LV-033",  # Gulbenes novads
    "LV-041",  # Jelgavas novads
    "LV-042",  # Jēkabpils novads
    "LV-047",  # Krāslavas novads
    "LV-050",  # Kuldīgas novads
    "LV-052",  # Ķekavas novads
    "LV-054",  # Limbažu novads
    "LV-056",  # Līvānu novads
    "LV-058",  # Ludzas novads
    "LV-059",  # Madonas novads
    "LV-062",  # Mārupes novads
    "LV-067",  # Ogres novads
    "LV-068",  # Olaines novads
    "LV-073",  # Preiļu novads
    "LV-077",  # Rēzeknes novads
    "LV-080",  # Ropažu novads
    "LV-087",  # Salaspils novads
    "LV-088",  # Saldus novads
    "LV-089",  # Saulkrastu novads
    "LV-091",  # Siguldas novads
    "LV-094",  # Smiltenes novads
    "LV-097",  # Talsu novads
    "LV-099",  # Tukuma novads
    "LV-101",  # Valkas novads
    "LV-102",  # Varakļānu novads
    "LV-106",  # Ventspils novads
    "LV-111",  # Augšdaugavas novads
    "LV-112",  # Dienvidkurzemes Novads
    "LV-113",  # Valmieras Novads
    "LV-DGV",  # Daugavpils
    "LV-JEL",  # Jelgava
    "LV-JUR",  # Jūrmala
    "LV-LPX",  # Liepāja
    "LV-REZ",  # Rēzekne
    "LV-RIX",  # Rīga
    "LV-VEN",  # Ventspils
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class LVSubdivision(Subdivision):
    code: LVSubdivisionCodeType


LV: Final[Country] = Country(
    alpha2="LV",
    alpha3="LVA",
    name="Latvia",
    common_name=None,
    official_name="Republic of Latvia",
    subdivisions=[
        LVSubdivision(code="LV-002", name="Aizkraukles novads", type_="Municipality"),
        LVSubdivision(code="LV-007", name="Alūksnes novads", type_="Municipality"),
        LVSubdivision(code="LV-011", name="Ādažu novads", type_="Municipality"),
        LVSubdivision(code="LV-015", name="Balvu novads", type_="Municipality"),
        LVSubdivision(code="LV-016", name="Bauskas novads", type_="Municipality"),
        LVSubdivision(code="LV-022", name="Cēsu novads", type_="Municipality"),
        LVSubdivision(code="LV-026", name="Dobeles novads", type_="Municipality"),
        LVSubdivision(code="LV-033", name="Gulbenes novads", type_="Municipality"),
        LVSubdivision(code="LV-041", name="Jelgavas novads", type_="Municipality"),
        LVSubdivision(code="LV-042", name="Jēkabpils novads", type_="Municipality"),
        LVSubdivision(code="LV-047", name="Krāslavas novads", type_="Municipality"),
        LVSubdivision(code="LV-050", name="Kuldīgas novads", type_="Municipality"),
        LVSubdivision(code="LV-052", name="Ķekavas novads", type_="Municipality"),
        LVSubdivision(code="LV-054", name="Limbažu novads", type_="Municipality"),
        LVSubdivision(code="LV-056", name="Līvānu novads", type_="Municipality"),
        LVSubdivision(code="LV-058", name="Ludzas novads", type_="Municipality"),
        LVSubdivision(code="LV-059", name="Madonas novads", type_="Municipality"),
        LVSubdivision(code="LV-062", name="Mārupes novads", type_="Municipality"),
        LVSubdivision(code="LV-067", name="Ogres novads", type_="Municipality"),
        LVSubdivision(code="LV-068", name="Olaines novads", type_="Municipality"),
        LVSubdivision(code="LV-073", name="Preiļu novads", type_="Municipality"),
        LVSubdivision(code="LV-077", name="Rēzeknes novads", type_="Municipality"),
        LVSubdivision(code="LV-080", name="Ropažu novads", type_="Municipality"),
        LVSubdivision(code="LV-087", name="Salaspils novads", type_="Municipality"),
        LVSubdivision(code="LV-088", name="Saldus novads", type_="Municipality"),
        LVSubdivision(code="LV-089", name="Saulkrastu novads", type_="Municipality"),
        LVSubdivision(code="LV-091", name="Siguldas novads", type_="Municipality"),
        LVSubdivision(code="LV-094", name="Smiltenes novads", type_="Municipality"),
        LVSubdivision(code="LV-097", name="Talsu novads", type_="Municipality"),
        LVSubdivision(code="LV-099", name="Tukuma novads", type_="Municipality"),
        LVSubdivision(code="LV-101", name="Valkas novads", type_="Municipality"),
        LVSubdivision(code="LV-102", name="Varakļānu novads", type_="Municipality"),
        LVSubdivision(code="LV-106", name="Ventspils novads", type_="Municipality"),
        LVSubdivision(code="LV-111", name="Augšdaugavas novads", type_="Municipality"),
        LVSubdivision(code="LV-112", name="Dienvidkurzemes Novads", type_="Municipality"),
        LVSubdivision(code="LV-113", name="Valmieras Novads", type_="Municipality"),
        LVSubdivision(code="LV-DGV", name="Daugavpils", type_="State city"),
        LVSubdivision(code="LV-JEL", name="Jelgava", type_="State city"),
        LVSubdivision(code="LV-JUR", name="Jūrmala", type_="State city"),
        LVSubdivision(code="LV-LPX", name="Liepāja", type_="State city"),
        LVSubdivision(code="LV-REZ", name="Rēzekne", type_="State city"),
        LVSubdivision(code="LV-RIX", name="Rīga", type_="State city"),
        LVSubdivision(code="LV-VEN", name="Ventspils", type_="State city"),
    ],
)
