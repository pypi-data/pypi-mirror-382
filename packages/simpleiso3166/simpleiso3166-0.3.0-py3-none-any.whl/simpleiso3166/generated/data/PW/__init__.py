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

PWSubdivisionCodeType = Literal[
    "PW-002",  # Aimeliik
    "PW-004",  # Airai
    "PW-010",  # Angaur
    "PW-050",  # Hatohobei
    "PW-100",  # Kayangel
    "PW-150",  # Koror
    "PW-212",  # Melekeok
    "PW-214",  # Ngaraard
    "PW-218",  # Ngarchelong
    "PW-222",  # Ngardmau
    "PW-224",  # Ngatpang
    "PW-226",  # Ngchesar
    "PW-227",  # Ngeremlengui
    "PW-228",  # Ngiwal
    "PW-350",  # Peleliu
    "PW-370",  # Sonsorol
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class PWSubdivision(Subdivision):
    code: PWSubdivisionCodeType


PW: Final[Country] = Country(
    alpha2="PW",
    alpha3="PLW",
    name="Palau",
    common_name=None,
    official_name="Republic of Palau",
    subdivisions=[
        PWSubdivision(code="PW-002", name="Aimeliik", type_="State"),
        PWSubdivision(code="PW-004", name="Airai", type_="State"),
        PWSubdivision(code="PW-010", name="Angaur", type_="State"),
        PWSubdivision(code="PW-050", name="Hatohobei", type_="State"),
        PWSubdivision(code="PW-100", name="Kayangel", type_="State"),
        PWSubdivision(code="PW-150", name="Koror", type_="State"),
        PWSubdivision(code="PW-212", name="Melekeok", type_="State"),
        PWSubdivision(code="PW-214", name="Ngaraard", type_="State"),
        PWSubdivision(code="PW-218", name="Ngarchelong", type_="State"),
        PWSubdivision(code="PW-222", name="Ngardmau", type_="State"),
        PWSubdivision(code="PW-224", name="Ngatpang", type_="State"),
        PWSubdivision(code="PW-226", name="Ngchesar", type_="State"),
        PWSubdivision(code="PW-227", name="Ngeremlengui", type_="State"),
        PWSubdivision(code="PW-228", name="Ngiwal", type_="State"),
        PWSubdivision(code="PW-350", name="Peleliu", type_="State"),
        PWSubdivision(code="PW-370", name="Sonsorol", type_="State"),
    ],
)
