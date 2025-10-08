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

NRSubdivisionCodeType = Literal[
    "NR-01",  # Aiwo
    "NR-02",  # Anabar
    "NR-03",  # Anetan
    "NR-04",  # Anibare
    "NR-05",  # Baitsi
    "NR-06",  # Boe
    "NR-07",  # Buada
    "NR-08",  # Denigomodu
    "NR-09",  # Ewa
    "NR-10",  # Ijuw
    "NR-11",  # Meneng
    "NR-12",  # Nibok
    "NR-13",  # Uaboe
    "NR-14",  # Yaren
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class NRSubdivision(Subdivision):
    code: NRSubdivisionCodeType


NR: Final[Country] = Country(
    alpha2="NR",
    alpha3="NRU",
    name="Nauru",
    common_name=None,
    official_name="Republic of Nauru",
    subdivisions=[
        NRSubdivision(code="NR-01", name="Aiwo", type_="District"),
        NRSubdivision(code="NR-02", name="Anabar", type_="District"),
        NRSubdivision(code="NR-03", name="Anetan", type_="District"),
        NRSubdivision(code="NR-04", name="Anibare", type_="District"),
        NRSubdivision(code="NR-05", name="Baitsi", type_="District"),
        NRSubdivision(code="NR-06", name="Boe", type_="District"),
        NRSubdivision(code="NR-07", name="Buada", type_="District"),
        NRSubdivision(code="NR-08", name="Denigomodu", type_="District"),
        NRSubdivision(code="NR-09", name="Ewa", type_="District"),
        NRSubdivision(code="NR-10", name="Ijuw", type_="District"),
        NRSubdivision(code="NR-11", name="Meneng", type_="District"),
        NRSubdivision(code="NR-12", name="Nibok", type_="District"),
        NRSubdivision(code="NR-13", name="Uaboe", type_="District"),
        NRSubdivision(code="NR-14", name="Yaren", type_="District"),
    ],
)
