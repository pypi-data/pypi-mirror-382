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

INSubdivisionCodeType = Literal[
    "IN-AN",  # Andaman and Nicobar Islands
    "IN-AP",  # Andhra Pradesh
    "IN-AR",  # Arunāchal Pradesh
    "IN-AS",  # Assam
    "IN-BR",  # Bihār
    "IN-CG",  # Chhattīsgarh
    "IN-CH",  # Chandīgarh
    "IN-DH",  # Dādra and Nagar Haveli and Damān and Diu
    "IN-DL",  # Delhi
    "IN-GA",  # Goa
    "IN-GJ",  # Gujarāt
    "IN-HP",  # Himāchal Pradesh
    "IN-HR",  # Haryāna
    "IN-JH",  # Jhārkhand
    "IN-JK",  # Jammu and Kashmīr
    "IN-KA",  # Karnātaka
    "IN-KL",  # Kerala
    "IN-LA",  # Ladākh
    "IN-LD",  # Lakshadweep
    "IN-MH",  # Mahārāshtra
    "IN-ML",  # Meghālaya
    "IN-MN",  # Manipur
    "IN-MP",  # Madhya Pradesh
    "IN-MZ",  # Mizoram
    "IN-NL",  # Nāgāland
    "IN-OD",  # Odisha
    "IN-PB",  # Punjab
    "IN-PY",  # Puducherry
    "IN-RJ",  # Rājasthān
    "IN-SK",  # Sikkim
    "IN-TN",  # Tamil Nādu
    "IN-TR",  # Tripura
    "IN-TS",  # Telangāna
    "IN-UK",  # Uttarākhand
    "IN-UP",  # Uttar Pradesh
    "IN-WB",  # West Bengal
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class INSubdivision(Subdivision):
    code: INSubdivisionCodeType


IN: Final[Country] = Country(
    alpha2="IN",
    alpha3="IND",
    name="India",
    common_name=None,
    official_name="Republic of India",
    subdivisions=[
        INSubdivision(code="IN-AN", name="Andaman and Nicobar Islands", type_="Union territory"),
        INSubdivision(code="IN-AP", name="Andhra Pradesh", type_="State"),
        INSubdivision(code="IN-AR", name="Arunāchal Pradesh", type_="State"),
        INSubdivision(code="IN-AS", name="Assam", type_="State"),
        INSubdivision(code="IN-BR", name="Bihār", type_="State"),
        INSubdivision(code="IN-CG", name="Chhattīsgarh", type_="State"),
        INSubdivision(code="IN-CH", name="Chandīgarh", type_="Union territory"),
        INSubdivision(code="IN-DH", name="Dādra and Nagar Haveli and Damān and Diu", type_="Union territory"),
        INSubdivision(code="IN-DL", name="Delhi", type_="Union territory"),
        INSubdivision(code="IN-GA", name="Goa", type_="State"),
        INSubdivision(code="IN-GJ", name="Gujarāt", type_="State"),
        INSubdivision(code="IN-HP", name="Himāchal Pradesh", type_="State"),
        INSubdivision(code="IN-HR", name="Haryāna", type_="State"),
        INSubdivision(code="IN-JH", name="Jhārkhand", type_="State"),
        INSubdivision(code="IN-JK", name="Jammu and Kashmīr", type_="Union territory"),
        INSubdivision(code="IN-KA", name="Karnātaka", type_="State"),
        INSubdivision(code="IN-KL", name="Kerala", type_="State"),
        INSubdivision(code="IN-LA", name="Ladākh", type_="Union territory"),
        INSubdivision(code="IN-LD", name="Lakshadweep", type_="Union territory"),
        INSubdivision(code="IN-MH", name="Mahārāshtra", type_="State"),
        INSubdivision(code="IN-ML", name="Meghālaya", type_="State"),
        INSubdivision(code="IN-MN", name="Manipur", type_="State"),
        INSubdivision(code="IN-MP", name="Madhya Pradesh", type_="State"),
        INSubdivision(code="IN-MZ", name="Mizoram", type_="State"),
        INSubdivision(code="IN-NL", name="Nāgāland", type_="State"),
        INSubdivision(code="IN-OD", name="Odisha", type_="State"),
        INSubdivision(code="IN-PB", name="Punjab", type_="State"),
        INSubdivision(code="IN-PY", name="Puducherry", type_="Union territory"),
        INSubdivision(code="IN-RJ", name="Rājasthān", type_="State"),
        INSubdivision(code="IN-SK", name="Sikkim", type_="State"),
        INSubdivision(code="IN-TN", name="Tamil Nādu", type_="State"),
        INSubdivision(code="IN-TR", name="Tripura", type_="State"),
        INSubdivision(code="IN-TS", name="Telangāna", type_="State"),
        INSubdivision(code="IN-UK", name="Uttarākhand", type_="State"),
        INSubdivision(code="IN-UP", name="Uttar Pradesh", type_="State"),
        INSubdivision(code="IN-WB", name="West Bengal", type_="State"),
    ],
)
