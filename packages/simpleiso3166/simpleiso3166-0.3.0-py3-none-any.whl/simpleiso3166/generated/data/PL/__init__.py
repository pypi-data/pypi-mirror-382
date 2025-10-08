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

PLSubdivisionCodeType = Literal[
    "PL-02",  # Dolnośląskie
    "PL-04",  # Kujawsko-Pomorskie
    "PL-06",  # Lubelskie
    "PL-08",  # Lubuskie
    "PL-10",  # Łódzkie
    "PL-12",  # Małopolskie
    "PL-14",  # Mazowieckie
    "PL-16",  # Opolskie
    "PL-18",  # Podkarpackie
    "PL-20",  # Podlaskie
    "PL-22",  # Pomorskie
    "PL-24",  # Śląskie
    "PL-26",  # Świętokrzyskie
    "PL-28",  # Warmińsko-Mazurskie
    "PL-30",  # Wielkopolskie
    "PL-32",  # Zachodniopomorskie
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class PLSubdivision(Subdivision):
    code: PLSubdivisionCodeType


PL: Final[Country] = Country(
    alpha2="PL",
    alpha3="POL",
    name="Poland",
    common_name=None,
    official_name="Republic of Poland",
    subdivisions=[
        PLSubdivision(code="PL-02", name="Dolnośląskie", type_="Voivodship"),
        PLSubdivision(code="PL-04", name="Kujawsko-Pomorskie", type_="Voivodship"),
        PLSubdivision(code="PL-06", name="Lubelskie", type_="Voivodship"),
        PLSubdivision(code="PL-08", name="Lubuskie", type_="Voivodship"),
        PLSubdivision(code="PL-10", name="Łódzkie", type_="Voivodship"),
        PLSubdivision(code="PL-12", name="Małopolskie", type_="Voivodship"),
        PLSubdivision(code="PL-14", name="Mazowieckie", type_="Voivodship"),
        PLSubdivision(code="PL-16", name="Opolskie", type_="Voivodship"),
        PLSubdivision(code="PL-18", name="Podkarpackie", type_="Voivodship"),
        PLSubdivision(code="PL-20", name="Podlaskie", type_="Voivodship"),
        PLSubdivision(code="PL-22", name="Pomorskie", type_="Voivodship"),
        PLSubdivision(code="PL-24", name="Śląskie", type_="Voivodship"),
        PLSubdivision(code="PL-26", name="Świętokrzyskie", type_="Voivodship"),
        PLSubdivision(code="PL-28", name="Warmińsko-Mazurskie", type_="Voivodship"),
        PLSubdivision(code="PL-30", name="Wielkopolskie", type_="Voivodship"),
        PLSubdivision(code="PL-32", name="Zachodniopomorskie", type_="Voivodship"),
    ],
)
