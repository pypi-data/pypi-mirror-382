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

LISubdivisionCodeType = Literal[
    "LI-01",  # Balzers
    "LI-02",  # Eschen
    "LI-03",  # Gamprin
    "LI-04",  # Mauren
    "LI-05",  # Planken
    "LI-06",  # Ruggell
    "LI-07",  # Schaan
    "LI-08",  # Schellenberg
    "LI-09",  # Triesen
    "LI-10",  # Triesenberg
    "LI-11",  # Vaduz
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class LISubdivision(Subdivision):
    code: LISubdivisionCodeType


LI: Final[Country] = Country(
    alpha2="LI",
    alpha3="LIE",
    name="Liechtenstein",
    common_name=None,
    official_name="Principality of Liechtenstein",
    subdivisions=[
        LISubdivision(code="LI-01", name="Balzers", type_="Commune"),
        LISubdivision(code="LI-02", name="Eschen", type_="Commune"),
        LISubdivision(code="LI-03", name="Gamprin", type_="Commune"),
        LISubdivision(code="LI-04", name="Mauren", type_="Commune"),
        LISubdivision(code="LI-05", name="Planken", type_="Commune"),
        LISubdivision(code="LI-06", name="Ruggell", type_="Commune"),
        LISubdivision(code="LI-07", name="Schaan", type_="Commune"),
        LISubdivision(code="LI-08", name="Schellenberg", type_="Commune"),
        LISubdivision(code="LI-09", name="Triesen", type_="Commune"),
        LISubdivision(code="LI-10", name="Triesenberg", type_="Commune"),
        LISubdivision(code="LI-11", name="Vaduz", type_="Commune"),
    ],
)
