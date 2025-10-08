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

ADSubdivisionCodeType = Literal[
    "AD-02",  # Canillo
    "AD-03",  # Encamp
    "AD-04",  # La Massana
    "AD-05",  # Ordino
    "AD-06",  # Sant Julià de Lòria
    "AD-07",  # Andorra la Vella
    "AD-08",  # Escaldes-Engordany
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class ADSubdivision(Subdivision):
    code: ADSubdivisionCodeType


AD: Final[Country] = Country(
    alpha2="AD",
    alpha3="AND",
    name="Andorra",
    common_name=None,
    official_name="Principality of Andorra",
    subdivisions=[
        ADSubdivision(code="AD-02", name="Canillo", type_="Parish"),
        ADSubdivision(code="AD-03", name="Encamp", type_="Parish"),
        ADSubdivision(code="AD-04", name="La Massana", type_="Parish"),
        ADSubdivision(code="AD-05", name="Ordino", type_="Parish"),
        ADSubdivision(code="AD-06", name="Sant Julià de Lòria", type_="Parish"),
        ADSubdivision(code="AD-07", name="Andorra la Vella", type_="Parish"),
        ADSubdivision(code="AD-08", name="Escaldes-Engordany", type_="Parish"),
    ],
)
