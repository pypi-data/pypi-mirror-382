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

KZSubdivisionCodeType = Literal[
    "KZ-10",  # Abajskaja oblast’
    "KZ-11",  # Akmolinskaja oblast'
    "KZ-15",  # Aktjubinskaja oblast'
    "KZ-19",  # Almatinskaja oblast'
    "KZ-23",  # Atyrauskaja oblast'
    "KZ-27",  # Batys Qazaqstan oblysy
    "KZ-31",  # Zhambyl oblysy
    "KZ-33",  # Zhetisū oblysy
    "KZ-35",  # Karagandinskaja oblast'
    "KZ-39",  # Kostanajskaja oblast'
    "KZ-43",  # Kyzylordinskaja oblast'
    "KZ-47",  # Mangghystaū oblysy
    "KZ-55",  # Pavlodar oblysy
    "KZ-59",  # Severo-Kazahstanskaja oblast'
    "KZ-61",  # Turkestankaya oblast'
    "KZ-62",  # Ulytauskaja oblast’
    "KZ-63",  # Shyghys Qazaqstan oblysy
    "KZ-71",  # Astana
    "KZ-75",  # Almaty
    "KZ-79",  # Shymkent
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class KZSubdivision(Subdivision):
    code: KZSubdivisionCodeType


KZ: Final[Country] = Country(
    alpha2="KZ",
    alpha3="KAZ",
    name="Kazakhstan",
    common_name=None,
    official_name="Republic of Kazakhstan",
    subdivisions=[
        KZSubdivision(code="KZ-10", name="Abajskaja oblast’", type_="Region"),
        KZSubdivision(code="KZ-11", name="Akmolinskaja oblast'", type_="Region"),
        KZSubdivision(code="KZ-15", name="Aktjubinskaja oblast'", type_="Region"),
        KZSubdivision(code="KZ-19", name="Almatinskaja oblast'", type_="Region"),
        KZSubdivision(code="KZ-23", name="Atyrauskaja oblast'", type_="Region"),
        KZSubdivision(code="KZ-27", name="Batys Qazaqstan oblysy", type_="Region"),
        KZSubdivision(code="KZ-31", name="Zhambyl oblysy", type_="Region"),
        KZSubdivision(code="KZ-33", name="Zhetisū oblysy", type_="Region"),
        KZSubdivision(code="KZ-35", name="Karagandinskaja oblast'", type_="Region"),
        KZSubdivision(code="KZ-39", name="Kostanajskaja oblast'", type_="Region"),
        KZSubdivision(code="KZ-43", name="Kyzylordinskaja oblast'", type_="Region"),
        KZSubdivision(code="KZ-47", name="Mangghystaū oblysy", type_="Region"),
        KZSubdivision(code="KZ-55", name="Pavlodar oblysy", type_="Region"),
        KZSubdivision(code="KZ-59", name="Severo-Kazahstanskaja oblast'", type_="Region"),
        KZSubdivision(code="KZ-61", name="Turkestankaya oblast'", type_="Region"),
        KZSubdivision(code="KZ-62", name="Ulytauskaja oblast’", type_="Region"),
        KZSubdivision(code="KZ-63", name="Shyghys Qazaqstan oblysy", type_="Region"),
        KZSubdivision(code="KZ-71", name="Astana", type_="City"),
        KZSubdivision(code="KZ-75", name="Almaty", type_="City"),
        KZSubdivision(code="KZ-79", name="Shymkent", type_="City"),
    ],
)
