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

MZSubdivisionCodeType = Literal[
    "MZ-A",  # Niassa
    "MZ-B",  # Manica
    "MZ-G",  # Gaza
    "MZ-I",  # Inhambane
    "MZ-L",  # Maputo
    "MZ-MPM",  # Maputo
    "MZ-N",  # Nampula
    "MZ-P",  # Cabo Delgado
    "MZ-Q",  # Zambézia
    "MZ-S",  # Sofala
    "MZ-T",  # Tete
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MZSubdivision(Subdivision):
    code: MZSubdivisionCodeType


MZ: Final[Country] = Country(
    alpha2="MZ",
    alpha3="MOZ",
    name="Mozambique",
    common_name=None,
    official_name="Republic of Mozambique",
    subdivisions=[
        MZSubdivision(code="MZ-A", name="Niassa", type_="Province"),
        MZSubdivision(code="MZ-B", name="Manica", type_="Province"),
        MZSubdivision(code="MZ-G", name="Gaza", type_="Province"),
        MZSubdivision(code="MZ-I", name="Inhambane", type_="Province"),
        MZSubdivision(code="MZ-L", name="Maputo", type_="Province"),
        MZSubdivision(code="MZ-MPM", name="Maputo", type_="City"),
        MZSubdivision(code="MZ-N", name="Nampula", type_="Province"),
        MZSubdivision(code="MZ-P", name="Cabo Delgado", type_="Province"),
        MZSubdivision(code="MZ-Q", name="Zambézia", type_="Province"),
        MZSubdivision(code="MZ-S", name="Sofala", type_="Province"),
        MZSubdivision(code="MZ-T", name="Tete", type_="Province"),
    ],
)
