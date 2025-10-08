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

TNSubdivisionCodeType = Literal[
    "TN-11",  # Tunis
    "TN-12",  # L'Ariana
    "TN-13",  # Ben Arous
    "TN-14",  # La Manouba
    "TN-21",  # Nabeul
    "TN-22",  # Zaghouan
    "TN-23",  # Bizerte
    "TN-31",  # Béja
    "TN-32",  # Jendouba
    "TN-33",  # Le Kef
    "TN-34",  # Siliana
    "TN-41",  # Kairouan
    "TN-42",  # Kasserine
    "TN-43",  # Sidi Bouzid
    "TN-51",  # Sousse
    "TN-52",  # Monastir
    "TN-53",  # Mahdia
    "TN-61",  # Sfax
    "TN-71",  # Gafsa
    "TN-72",  # Tozeur
    "TN-73",  # Kébili
    "TN-81",  # Gabès
    "TN-82",  # Médenine
    "TN-83",  # Tataouine
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class TNSubdivision(Subdivision):
    code: TNSubdivisionCodeType


TN: Final[Country] = Country(
    alpha2="TN",
    alpha3="TUN",
    name="Tunisia",
    common_name=None,
    official_name="Republic of Tunisia",
    subdivisions=[
        TNSubdivision(code="TN-11", name="Tunis", type_="Governorate"),
        TNSubdivision(code="TN-12", name="L'Ariana", type_="Governorate"),
        TNSubdivision(code="TN-13", name="Ben Arous", type_="Governorate"),
        TNSubdivision(code="TN-14", name="La Manouba", type_="Governorate"),
        TNSubdivision(code="TN-21", name="Nabeul", type_="Governorate"),
        TNSubdivision(code="TN-22", name="Zaghouan", type_="Governorate"),
        TNSubdivision(code="TN-23", name="Bizerte", type_="Governorate"),
        TNSubdivision(code="TN-31", name="Béja", type_="Governorate"),
        TNSubdivision(code="TN-32", name="Jendouba", type_="Governorate"),
        TNSubdivision(code="TN-33", name="Le Kef", type_="Governorate"),
        TNSubdivision(code="TN-34", name="Siliana", type_="Governorate"),
        TNSubdivision(code="TN-41", name="Kairouan", type_="Governorate"),
        TNSubdivision(code="TN-42", name="Kasserine", type_="Governorate"),
        TNSubdivision(code="TN-43", name="Sidi Bouzid", type_="Governorate"),
        TNSubdivision(code="TN-51", name="Sousse", type_="Governorate"),
        TNSubdivision(code="TN-52", name="Monastir", type_="Governorate"),
        TNSubdivision(code="TN-53", name="Mahdia", type_="Governorate"),
        TNSubdivision(code="TN-61", name="Sfax", type_="Governorate"),
        TNSubdivision(code="TN-71", name="Gafsa", type_="Governorate"),
        TNSubdivision(code="TN-72", name="Tozeur", type_="Governorate"),
        TNSubdivision(code="TN-73", name="Kébili", type_="Governorate"),
        TNSubdivision(code="TN-81", name="Gabès", type_="Governorate"),
        TNSubdivision(code="TN-82", name="Médenine", type_="Governorate"),
        TNSubdivision(code="TN-83", name="Tataouine", type_="Governorate"),
    ],
)
