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

MNSubdivisionCodeType = Literal[
    "MN-035",  # Orhon
    "MN-037",  # Darhan uul
    "MN-039",  # Hentiy
    "MN-041",  # Hövsgöl
    "MN-043",  # Hovd
    "MN-046",  # Uvs
    "MN-047",  # Töv
    "MN-049",  # Selenge
    "MN-051",  # Sühbaatar
    "MN-053",  # Ömnögovĭ
    "MN-055",  # Övörhangay
    "MN-057",  # Dzavhan
    "MN-059",  # Dundgovĭ
    "MN-061",  # Dornod
    "MN-063",  # Dornogovĭ
    "MN-064",  # Govĭ-Sümber
    "MN-065",  # Govĭ-Altay
    "MN-067",  # Bulgan
    "MN-069",  # Bayanhongor
    "MN-071",  # Bayan-Ölgiy
    "MN-073",  # Arhangay
    "MN-1",  # Ulaanbaatar
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MNSubdivision(Subdivision):
    code: MNSubdivisionCodeType


MN: Final[Country] = Country(
    alpha2="MN",
    alpha3="MNG",
    name="Mongolia",
    common_name=None,
    official_name=None,
    subdivisions=[
        MNSubdivision(code="MN-035", name="Orhon", type_="Province"),
        MNSubdivision(code="MN-037", name="Darhan uul", type_="Province"),
        MNSubdivision(code="MN-039", name="Hentiy", type_="Province"),
        MNSubdivision(code="MN-041", name="Hövsgöl", type_="Province"),
        MNSubdivision(code="MN-043", name="Hovd", type_="Province"),
        MNSubdivision(code="MN-046", name="Uvs", type_="Province"),
        MNSubdivision(code="MN-047", name="Töv", type_="Province"),
        MNSubdivision(code="MN-049", name="Selenge", type_="Province"),
        MNSubdivision(code="MN-051", name="Sühbaatar", type_="Province"),
        MNSubdivision(code="MN-053", name="Ömnögovĭ", type_="Province"),
        MNSubdivision(code="MN-055", name="Övörhangay", type_="Province"),
        MNSubdivision(code="MN-057", name="Dzavhan", type_="Province"),
        MNSubdivision(code="MN-059", name="Dundgovĭ", type_="Province"),
        MNSubdivision(code="MN-061", name="Dornod", type_="Province"),
        MNSubdivision(code="MN-063", name="Dornogovĭ", type_="Province"),
        MNSubdivision(code="MN-064", name="Govĭ-Sümber", type_="Province"),
        MNSubdivision(code="MN-065", name="Govĭ-Altay", type_="Province"),
        MNSubdivision(code="MN-067", name="Bulgan", type_="Province"),
        MNSubdivision(code="MN-069", name="Bayanhongor", type_="Province"),
        MNSubdivision(code="MN-071", name="Bayan-Ölgiy", type_="Province"),
        MNSubdivision(code="MN-073", name="Arhangay", type_="Province"),
        MNSubdivision(code="MN-1", name="Ulaanbaatar", type_="Capital city"),
    ],
)
