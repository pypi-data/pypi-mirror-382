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

LKSubdivisionCodeType = Literal[
    "LK-1",  # Western Province
    "LK-11",  # Colombo
    "LK-12",  # Gampaha
    "LK-13",  # Kalutara
    "LK-2",  # Central Province
    "LK-21",  # Kandy
    "LK-22",  # Matale
    "LK-23",  # Nuwara Eliya
    "LK-3",  # Southern Province
    "LK-31",  # Galle
    "LK-32",  # Matara
    "LK-33",  # Hambantota
    "LK-4",  # Northern Province
    "LK-41",  # Jaffna
    "LK-42",  # Kilinochchi
    "LK-43",  # Mannar
    "LK-44",  # Vavuniya
    "LK-45",  # Mullaittivu
    "LK-5",  # Eastern Province
    "LK-51",  # Batticaloa
    "LK-52",  # Ampara
    "LK-53",  # Trincomalee
    "LK-6",  # North Western Province
    "LK-61",  # Kurunegala
    "LK-62",  # Puttalam
    "LK-7",  # North Central Province
    "LK-71",  # Anuradhapura
    "LK-72",  # Polonnaruwa
    "LK-8",  # Uva Province
    "LK-81",  # Badulla
    "LK-82",  # Monaragala
    "LK-9",  # Sabaragamuwa Province
    "LK-91",  # Ratnapura
    "LK-92",  # Kegalla
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class LKSubdivision(Subdivision):
    code: LKSubdivisionCodeType


LK: Final[Country] = Country(
    alpha2="LK",
    alpha3="LKA",
    name="Sri Lanka",
    common_name=None,
    official_name="Democratic Socialist Republic of Sri Lanka",
    subdivisions=[
        LKSubdivision(code="LK-1", name="Western Province", type_="Province"),
        LKSubdivision(code="LK-11", name="Colombo", type_="District"),
        LKSubdivision(code="LK-12", name="Gampaha", type_="District"),
        LKSubdivision(code="LK-13", name="Kalutara", type_="District"),
        LKSubdivision(code="LK-2", name="Central Province", type_="Province"),
        LKSubdivision(code="LK-21", name="Kandy", type_="District"),
        LKSubdivision(code="LK-22", name="Matale", type_="District"),
        LKSubdivision(code="LK-23", name="Nuwara Eliya", type_="District"),
        LKSubdivision(code="LK-3", name="Southern Province", type_="Province"),
        LKSubdivision(code="LK-31", name="Galle", type_="District"),
        LKSubdivision(code="LK-32", name="Matara", type_="District"),
        LKSubdivision(code="LK-33", name="Hambantota", type_="District"),
        LKSubdivision(code="LK-4", name="Northern Province", type_="Province"),
        LKSubdivision(code="LK-41", name="Jaffna", type_="District"),
        LKSubdivision(code="LK-42", name="Kilinochchi", type_="District"),
        LKSubdivision(code="LK-43", name="Mannar", type_="District"),
        LKSubdivision(code="LK-44", name="Vavuniya", type_="District"),
        LKSubdivision(code="LK-45", name="Mullaittivu", type_="District"),
        LKSubdivision(code="LK-5", name="Eastern Province", type_="Province"),
        LKSubdivision(code="LK-51", name="Batticaloa", type_="District"),
        LKSubdivision(code="LK-52", name="Ampara", type_="District"),
        LKSubdivision(code="LK-53", name="Trincomalee", type_="District"),
        LKSubdivision(code="LK-6", name="North Western Province", type_="Province"),
        LKSubdivision(code="LK-61", name="Kurunegala", type_="District"),
        LKSubdivision(code="LK-62", name="Puttalam", type_="District"),
        LKSubdivision(code="LK-7", name="North Central Province", type_="Province"),
        LKSubdivision(code="LK-71", name="Anuradhapura", type_="District"),
        LKSubdivision(code="LK-72", name="Polonnaruwa", type_="District"),
        LKSubdivision(code="LK-8", name="Uva Province", type_="Province"),
        LKSubdivision(code="LK-81", name="Badulla", type_="District"),
        LKSubdivision(code="LK-82", name="Monaragala", type_="District"),
        LKSubdivision(code="LK-9", name="Sabaragamuwa Province", type_="Province"),
        LKSubdivision(code="LK-91", name="Ratnapura", type_="District"),
        LKSubdivision(code="LK-92", name="Kegalla", type_="District"),
    ],
)
