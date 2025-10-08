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

MUSubdivisionCodeType = Literal[
    "MU-AG",  # Agalega Islands
    "MU-BL",  # Black River
    "MU-CC",  # Cargados Carajos Shoals
    "MU-FL",  # Flacq
    "MU-GP",  # Grand Port
    "MU-MO",  # Moka
    "MU-PA",  # Pamplemousses
    "MU-PL",  # Port Louis
    "MU-PW",  # Plaines Wilhems
    "MU-RO",  # Rodrigues Island
    "MU-RR",  # Rivière du Rempart
    "MU-SA",  # Savanne
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MUSubdivision(Subdivision):
    code: MUSubdivisionCodeType


MU: Final[Country] = Country(
    alpha2="MU",
    alpha3="MUS",
    name="Mauritius",
    common_name=None,
    official_name="Republic of Mauritius",
    subdivisions=[
        MUSubdivision(code="MU-AG", name="Agalega Islands", type_="Dependency"),
        MUSubdivision(code="MU-BL", name="Black River", type_="District"),
        MUSubdivision(code="MU-CC", name="Cargados Carajos Shoals", type_="Dependency"),
        MUSubdivision(code="MU-FL", name="Flacq", type_="District"),
        MUSubdivision(code="MU-GP", name="Grand Port", type_="District"),
        MUSubdivision(code="MU-MO", name="Moka", type_="District"),
        MUSubdivision(code="MU-PA", name="Pamplemousses", type_="District"),
        MUSubdivision(code="MU-PL", name="Port Louis", type_="District"),
        MUSubdivision(code="MU-PW", name="Plaines Wilhems", type_="District"),
        MUSubdivision(code="MU-RO", name="Rodrigues Island", type_="Dependency"),
        MUSubdivision(code="MU-RR", name="Rivière du Rempart", type_="District"),
        MUSubdivision(code="MU-SA", name="Savanne", type_="District"),
    ],
)
