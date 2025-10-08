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

PASubdivisionCodeType = Literal[
    "PA-1",  # Bocas del Toro
    "PA-10",  # Panamá Oeste
    "PA-2",  # Coclé
    "PA-3",  # Colón
    "PA-4",  # Chiriquí
    "PA-5",  # Darién
    "PA-6",  # Herrera
    "PA-7",  # Los Santos
    "PA-8",  # Panamá
    "PA-9",  # Veraguas
    "PA-EM",  # Emberá
    "PA-KY",  # Guna Yala
    "PA-NB",  # Ngäbe-Buglé
    "PA-NT",  # Naso Tjër Di
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class PASubdivision(Subdivision):
    code: PASubdivisionCodeType


PA: Final[Country] = Country(
    alpha2="PA",
    alpha3="PAN",
    name="Panama",
    common_name=None,
    official_name="Republic of Panama",
    subdivisions=[
        PASubdivision(code="PA-1", name="Bocas del Toro", type_="Province"),
        PASubdivision(code="PA-10", name="Panamá Oeste", type_="Province"),
        PASubdivision(code="PA-2", name="Coclé", type_="Province"),
        PASubdivision(code="PA-3", name="Colón", type_="Province"),
        PASubdivision(code="PA-4", name="Chiriquí", type_="Province"),
        PASubdivision(code="PA-5", name="Darién", type_="Province"),
        PASubdivision(code="PA-6", name="Herrera", type_="Province"),
        PASubdivision(code="PA-7", name="Los Santos", type_="Province"),
        PASubdivision(code="PA-8", name="Panamá", type_="Province"),
        PASubdivision(code="PA-9", name="Veraguas", type_="Province"),
        PASubdivision(code="PA-EM", name="Emberá", type_="Indigenous region"),
        PASubdivision(code="PA-KY", name="Guna Yala", type_="Indigenous region"),
        PASubdivision(code="PA-NB", name="Ngäbe-Buglé", type_="Indigenous region"),
        PASubdivision(code="PA-NT", name="Naso Tjër Di", type_="Indigenous region"),
    ],
)
