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

DESubdivisionCodeType = Literal[
    "DE-BB",  # Brandenburg
    "DE-BE",  # Berlin
    "DE-BW",  # Baden-Württemberg
    "DE-BY",  # Bayern
    "DE-HB",  # Bremen
    "DE-HE",  # Hessen
    "DE-HH",  # Hamburg
    "DE-MV",  # Mecklenburg-Vorpommern
    "DE-NI",  # Niedersachsen
    "DE-NW",  # Nordrhein-Westfalen
    "DE-RP",  # Rheinland-Pfalz
    "DE-SH",  # Schleswig-Holstein
    "DE-SL",  # Saarland
    "DE-SN",  # Sachsen
    "DE-ST",  # Sachsen-Anhalt
    "DE-TH",  # Thüringen
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class DESubdivision(Subdivision):
    code: DESubdivisionCodeType


DE: Final[Country] = Country(
    alpha2="DE",
    alpha3="DEU",
    name="Germany",
    common_name=None,
    official_name="Federal Republic of Germany",
    subdivisions=[
        DESubdivision(code="DE-BB", name="Brandenburg", type_="Land"),
        DESubdivision(code="DE-BE", name="Berlin", type_="Land"),
        DESubdivision(code="DE-BW", name="Baden-Württemberg", type_="Land"),
        DESubdivision(code="DE-BY", name="Bayern", type_="Land"),
        DESubdivision(code="DE-HB", name="Bremen", type_="Land"),
        DESubdivision(code="DE-HE", name="Hessen", type_="Land"),
        DESubdivision(code="DE-HH", name="Hamburg", type_="Land"),
        DESubdivision(code="DE-MV", name="Mecklenburg-Vorpommern", type_="Land"),
        DESubdivision(code="DE-NI", name="Niedersachsen", type_="Land"),
        DESubdivision(code="DE-NW", name="Nordrhein-Westfalen", type_="Land"),
        DESubdivision(code="DE-RP", name="Rheinland-Pfalz", type_="Land"),
        DESubdivision(code="DE-SH", name="Schleswig-Holstein", type_="Land"),
        DESubdivision(code="DE-SL", name="Saarland", type_="Land"),
        DESubdivision(code="DE-SN", name="Sachsen", type_="Land"),
        DESubdivision(code="DE-ST", name="Sachsen-Anhalt", type_="Land"),
        DESubdivision(code="DE-TH", name="Thüringen", type_="Land"),
    ],
)
