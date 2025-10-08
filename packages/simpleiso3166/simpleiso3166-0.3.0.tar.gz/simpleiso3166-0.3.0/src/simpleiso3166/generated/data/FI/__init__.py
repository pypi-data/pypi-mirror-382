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

FISubdivisionCodeType = Literal[
    "FI-01",  # Landskapet Åland
    "FI-02",  # Etelä-Karjala
    "FI-03",  # Etelä-Pohjanmaa
    "FI-04",  # Etelä-Savo
    "FI-05",  # Kainuu
    "FI-06",  # Kanta-Häme
    "FI-07",  # Keski-Pohjanmaa
    "FI-08",  # Keski-Suomi
    "FI-09",  # Kymenlaakso
    "FI-10",  # Lappi
    "FI-11",  # Pirkanmaa
    "FI-12",  # Pohjanmaa
    "FI-13",  # Pohjois-Karjala
    "FI-14",  # Pohjois-Pohjanmaa
    "FI-15",  # Pohjois-Savo
    "FI-16",  # Päijät-Häme
    "FI-17",  # Satakunta
    "FI-18",  # Uusimaa
    "FI-19",  # Varsinais-Suomi
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class FISubdivision(Subdivision):
    code: FISubdivisionCodeType


FI: Final[Country] = Country(
    alpha2="FI",
    alpha3="FIN",
    name="Finland",
    common_name=None,
    official_name="Republic of Finland",
    subdivisions=[
        FISubdivision(code="FI-01", name="Landskapet Åland", type_="Region"),
        FISubdivision(code="FI-02", name="Etelä-Karjala", type_="Region"),
        FISubdivision(code="FI-03", name="Etelä-Pohjanmaa", type_="Region"),
        FISubdivision(code="FI-04", name="Etelä-Savo", type_="Region"),
        FISubdivision(code="FI-05", name="Kainuu", type_="Region"),
        FISubdivision(code="FI-06", name="Kanta-Häme", type_="Region"),
        FISubdivision(code="FI-07", name="Keski-Pohjanmaa", type_="Region"),
        FISubdivision(code="FI-08", name="Keski-Suomi", type_="Region"),
        FISubdivision(code="FI-09", name="Kymenlaakso", type_="Region"),
        FISubdivision(code="FI-10", name="Lappi", type_="Region"),
        FISubdivision(code="FI-11", name="Pirkanmaa", type_="Region"),
        FISubdivision(code="FI-12", name="Pohjanmaa", type_="Region"),
        FISubdivision(code="FI-13", name="Pohjois-Karjala", type_="Region"),
        FISubdivision(code="FI-14", name="Pohjois-Pohjanmaa", type_="Region"),
        FISubdivision(code="FI-15", name="Pohjois-Savo", type_="Region"),
        FISubdivision(code="FI-16", name="Päijät-Häme", type_="Region"),
        FISubdivision(code="FI-17", name="Satakunta", type_="Region"),
        FISubdivision(code="FI-18", name="Uusimaa", type_="Region"),
        FISubdivision(code="FI-19", name="Varsinais-Suomi", type_="Region"),
    ],
)
