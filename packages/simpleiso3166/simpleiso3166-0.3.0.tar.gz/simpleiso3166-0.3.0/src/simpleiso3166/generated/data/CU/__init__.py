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

CUSubdivisionCodeType = Literal[
    "CU-01",  # Pinar del Río
    "CU-03",  # La Habana
    "CU-04",  # Matanzas
    "CU-05",  # Villa Clara
    "CU-06",  # Cienfuegos
    "CU-07",  # Sancti Spíritus
    "CU-08",  # Ciego de Ávila
    "CU-09",  # Camagüey
    "CU-10",  # Las Tunas
    "CU-11",  # Holguín
    "CU-12",  # Granma
    "CU-13",  # Santiago de Cuba
    "CU-14",  # Guantánamo
    "CU-15",  # Artemisa
    "CU-16",  # Mayabeque
    "CU-99",  # Isla de la Juventud
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class CUSubdivision(Subdivision):
    code: CUSubdivisionCodeType


CU: Final[Country] = Country(
    alpha2="CU",
    alpha3="CUB",
    name="Cuba",
    common_name=None,
    official_name="Republic of Cuba",
    subdivisions=[
        CUSubdivision(code="CU-01", name="Pinar del Río", type_="Province"),
        CUSubdivision(code="CU-03", name="La Habana", type_="Province"),
        CUSubdivision(code="CU-04", name="Matanzas", type_="Province"),
        CUSubdivision(code="CU-05", name="Villa Clara", type_="Province"),
        CUSubdivision(code="CU-06", name="Cienfuegos", type_="Province"),
        CUSubdivision(code="CU-07", name="Sancti Spíritus", type_="Province"),
        CUSubdivision(code="CU-08", name="Ciego de Ávila", type_="Province"),
        CUSubdivision(code="CU-09", name="Camagüey", type_="Province"),
        CUSubdivision(code="CU-10", name="Las Tunas", type_="Province"),
        CUSubdivision(code="CU-11", name="Holguín", type_="Province"),
        CUSubdivision(code="CU-12", name="Granma", type_="Province"),
        CUSubdivision(code="CU-13", name="Santiago de Cuba", type_="Province"),
        CUSubdivision(code="CU-14", name="Guantánamo", type_="Province"),
        CUSubdivision(code="CU-15", name="Artemisa", type_="Province"),
        CUSubdivision(code="CU-16", name="Mayabeque", type_="Province"),
        CUSubdivision(code="CU-99", name="Isla de la Juventud", type_="Special municipality"),
    ],
)
