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

PSSubdivisionCodeType = Literal[
    "PS-BTH",  # Bethlehem
    "PS-DEB",  # Deir El Balah
    "PS-GZA",  # Gaza
    "PS-HBN",  # Hebron
    "PS-JEM",  # Jerusalem
    "PS-JEN",  # Jenin
    "PS-JRH",  # Jericho and Al Aghwar
    "PS-KYS",  # Khan Yunis
    "PS-NBS",  # Nablus
    "PS-NGZ",  # North Gaza
    "PS-QQA",  # Qalqilya
    "PS-RBH",  # Ramallah
    "PS-RFH",  # Rafah
    "PS-SLT",  # Salfit
    "PS-TBS",  # Tubas
    "PS-TKM",  # Tulkarm
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class PSSubdivision(Subdivision):
    code: PSSubdivisionCodeType


PS: Final[Country] = Country(
    alpha2="PS",
    alpha3="PSE",
    name="Palestine, State of",
    common_name=None,
    official_name="the State of Palestine",
    subdivisions=[
        PSSubdivision(code="PS-BTH", name="Bethlehem", type_="Governorate"),
        PSSubdivision(code="PS-DEB", name="Deir El Balah", type_="Governorate"),
        PSSubdivision(code="PS-GZA", name="Gaza", type_="Governorate"),
        PSSubdivision(code="PS-HBN", name="Hebron", type_="Governorate"),
        PSSubdivision(code="PS-JEM", name="Jerusalem", type_="Governorate"),
        PSSubdivision(code="PS-JEN", name="Jenin", type_="Governorate"),
        PSSubdivision(code="PS-JRH", name="Jericho and Al Aghwar", type_="Governorate"),
        PSSubdivision(code="PS-KYS", name="Khan Yunis", type_="Governorate"),
        PSSubdivision(code="PS-NBS", name="Nablus", type_="Governorate"),
        PSSubdivision(code="PS-NGZ", name="North Gaza", type_="Governorate"),
        PSSubdivision(code="PS-QQA", name="Qalqilya", type_="Governorate"),
        PSSubdivision(code="PS-RBH", name="Ramallah", type_="Governorate"),
        PSSubdivision(code="PS-RFH", name="Rafah", type_="Governorate"),
        PSSubdivision(code="PS-SLT", name="Salfit", type_="Governorate"),
        PSSubdivision(code="PS-TBS", name="Tubas", type_="Governorate"),
        PSSubdivision(code="PS-TKM", name="Tulkarm", type_="Governorate"),
    ],
)
