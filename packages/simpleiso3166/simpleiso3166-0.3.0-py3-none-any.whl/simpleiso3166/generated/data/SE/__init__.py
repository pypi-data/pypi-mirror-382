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

SESubdivisionCodeType = Literal[
    "SE-AB",  # Stockholms län [SE-01]
    "SE-AC",  # Västerbottens län [SE-24]
    "SE-BD",  # Norrbottens län [SE-25]
    "SE-C",  # Uppsala län [SE-03]
    "SE-D",  # Södermanlands län [SE-04]
    "SE-E",  # Östergötlands län [SE-05]
    "SE-F",  # Jönköpings län [SE-06]
    "SE-G",  # Kronobergs län [SE-07]
    "SE-H",  # Kalmar län [SE-08]
    "SE-I",  # Gotlands län [SE-09]
    "SE-K",  # Blekinge län [SE-10]
    "SE-M",  # Skåne län [SE-12]
    "SE-N",  # Hallands län [SE-13]
    "SE-O",  # Västra Götalands län [SE-14]
    "SE-S",  # Värmlands län [SE-17]
    "SE-T",  # Örebro län [SE-18]
    "SE-U",  # Västmanlands län [SE-19]
    "SE-W",  # Dalarnas län [SE-20]
    "SE-X",  # Gävleborgs län [SE-21]
    "SE-Y",  # Västernorrlands län [SE-22]
    "SE-Z",  # Jämtlands län [SE-23]
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SESubdivision(Subdivision):
    code: SESubdivisionCodeType


SE: Final[Country] = Country(
    alpha2="SE",
    alpha3="SWE",
    name="Sweden",
    common_name=None,
    official_name="Kingdom of Sweden",
    subdivisions=[
        SESubdivision(code="SE-AB", name="Stockholms län [SE-01]", type_="County"),
        SESubdivision(code="SE-AC", name="Västerbottens län [SE-24]", type_="County"),
        SESubdivision(code="SE-BD", name="Norrbottens län [SE-25]", type_="County"),
        SESubdivision(code="SE-C", name="Uppsala län [SE-03]", type_="County"),
        SESubdivision(code="SE-D", name="Södermanlands län [SE-04]", type_="County"),
        SESubdivision(code="SE-E", name="Östergötlands län [SE-05]", type_="County"),
        SESubdivision(code="SE-F", name="Jönköpings län [SE-06]", type_="County"),
        SESubdivision(code="SE-G", name="Kronobergs län [SE-07]", type_="County"),
        SESubdivision(code="SE-H", name="Kalmar län [SE-08]", type_="County"),
        SESubdivision(code="SE-I", name="Gotlands län [SE-09]", type_="County"),
        SESubdivision(code="SE-K", name="Blekinge län [SE-10]", type_="County"),
        SESubdivision(code="SE-M", name="Skåne län [SE-12]", type_="County"),
        SESubdivision(code="SE-N", name="Hallands län [SE-13]", type_="County"),
        SESubdivision(code="SE-O", name="Västra Götalands län [SE-14]", type_="County"),
        SESubdivision(code="SE-S", name="Värmlands län [SE-17]", type_="County"),
        SESubdivision(code="SE-T", name="Örebro län [SE-18]", type_="County"),
        SESubdivision(code="SE-U", name="Västmanlands län [SE-19]", type_="County"),
        SESubdivision(code="SE-W", name="Dalarnas län [SE-20]", type_="County"),
        SESubdivision(code="SE-X", name="Gävleborgs län [SE-21]", type_="County"),
        SESubdivision(code="SE-Y", name="Västernorrlands län [SE-22]", type_="County"),
        SESubdivision(code="SE-Z", name="Jämtlands län [SE-23]", type_="County"),
    ],
)
