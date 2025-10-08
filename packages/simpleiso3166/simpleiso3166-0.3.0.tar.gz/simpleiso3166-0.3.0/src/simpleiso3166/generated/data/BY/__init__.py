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

BYSubdivisionCodeType = Literal[
    "BY-BR",  # Bresckaja voblasć
    "BY-HM",  # Gorod Minsk
    "BY-HO",  # Gomel'skaja oblast'
    "BY-HR",  # Grodnenskaja oblast'
    "BY-MA",  # Mahilioŭskaja voblasć
    "BY-MI",  # Minskaja oblast'
    "BY-VI",  # Viciebskaja voblasć
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BYSubdivision(Subdivision):
    code: BYSubdivisionCodeType


BY: Final[Country] = Country(
    alpha2="BY",
    alpha3="BLR",
    name="Belarus",
    common_name=None,
    official_name="Republic of Belarus",
    subdivisions=[
        BYSubdivision(code="BY-BR", name="Bresckaja voblasć", type_="Oblast"),
        BYSubdivision(code="BY-HM", name="Gorod Minsk", type_="City"),
        BYSubdivision(code="BY-HO", name="Gomel'skaja oblast'", type_="Oblast"),
        BYSubdivision(code="BY-HR", name="Grodnenskaja oblast'", type_="Oblast"),
        BYSubdivision(code="BY-MA", name="Mahilioŭskaja voblasć", type_="Oblast"),
        BYSubdivision(code="BY-MI", name="Minskaja oblast'", type_="Oblast"),
        BYSubdivision(code="BY-VI", name="Viciebskaja voblasć", type_="Oblast"),
    ],
)
