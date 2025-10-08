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

MYSubdivisionCodeType = Literal[
    "MY-01",  # Johor
    "MY-02",  # Kedah
    "MY-03",  # Kelantan
    "MY-04",  # Melaka
    "MY-05",  # Negeri Sembilan
    "MY-06",  # Pahang
    "MY-07",  # Pulau Pinang
    "MY-08",  # Perak
    "MY-09",  # Perlis
    "MY-10",  # Selangor
    "MY-11",  # Terengganu
    "MY-12",  # Sabah
    "MY-13",  # Sarawak
    "MY-14",  # Wilayah Persekutuan Kuala Lumpur
    "MY-15",  # Wilayah Persekutuan Labuan
    "MY-16",  # Wilayah Persekutuan Putrajaya
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MYSubdivision(Subdivision):
    code: MYSubdivisionCodeType


MY: Final[Country] = Country(
    alpha2="MY",
    alpha3="MYS",
    name="Malaysia",
    common_name=None,
    official_name=None,
    subdivisions=[
        MYSubdivision(code="MY-01", name="Johor", type_="State"),
        MYSubdivision(code="MY-02", name="Kedah", type_="State"),
        MYSubdivision(code="MY-03", name="Kelantan", type_="State"),
        MYSubdivision(code="MY-04", name="Melaka", type_="State"),
        MYSubdivision(code="MY-05", name="Negeri Sembilan", type_="State"),
        MYSubdivision(code="MY-06", name="Pahang", type_="State"),
        MYSubdivision(code="MY-07", name="Pulau Pinang", type_="State"),
        MYSubdivision(code="MY-08", name="Perak", type_="State"),
        MYSubdivision(code="MY-09", name="Perlis", type_="State"),
        MYSubdivision(code="MY-10", name="Selangor", type_="State"),
        MYSubdivision(code="MY-11", name="Terengganu", type_="State"),
        MYSubdivision(code="MY-12", name="Sabah", type_="State"),
        MYSubdivision(code="MY-13", name="Sarawak", type_="State"),
        MYSubdivision(code="MY-14", name="Wilayah Persekutuan Kuala Lumpur", type_="Federal territory"),
        MYSubdivision(code="MY-15", name="Wilayah Persekutuan Labuan", type_="Federal territory"),
        MYSubdivision(code="MY-16", name="Wilayah Persekutuan Putrajaya", type_="Federal territory"),
    ],
)
