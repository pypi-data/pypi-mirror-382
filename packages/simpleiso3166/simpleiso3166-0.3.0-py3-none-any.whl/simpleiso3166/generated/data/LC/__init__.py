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

LCSubdivisionCodeType = Literal[
    "LC-01",  # Anse la Raye
    "LC-02",  # Castries
    "LC-03",  # Choiseul
    "LC-05",  # Dennery
    "LC-06",  # Gros Islet
    "LC-07",  # Laborie
    "LC-08",  # Micoud
    "LC-10",  # Soufrière
    "LC-11",  # Vieux Fort
    "LC-12",  # Canaries
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class LCSubdivision(Subdivision):
    code: LCSubdivisionCodeType


LC: Final[Country] = Country(
    alpha2="LC",
    alpha3="LCA",
    name="Saint Lucia",
    common_name=None,
    official_name=None,
    subdivisions=[
        LCSubdivision(code="LC-01", name="Anse la Raye", type_="District"),
        LCSubdivision(code="LC-02", name="Castries", type_="District"),
        LCSubdivision(code="LC-03", name="Choiseul", type_="District"),
        LCSubdivision(code="LC-05", name="Dennery", type_="District"),
        LCSubdivision(code="LC-06", name="Gros Islet", type_="District"),
        LCSubdivision(code="LC-07", name="Laborie", type_="District"),
        LCSubdivision(code="LC-08", name="Micoud", type_="District"),
        LCSubdivision(code="LC-10", name="Soufrière", type_="District"),
        LCSubdivision(code="LC-11", name="Vieux Fort", type_="District"),
        LCSubdivision(code="LC-12", name="Canaries", type_="District"),
    ],
)
