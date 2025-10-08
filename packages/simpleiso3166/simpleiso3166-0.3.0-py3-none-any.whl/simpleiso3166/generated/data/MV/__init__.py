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

MVSubdivisionCodeType = Literal[
    "MV-00",  # South Ari Atoll
    "MV-01",  # Addu City
    "MV-02",  # North Ari Atoll
    "MV-03",  # Faadhippolhu
    "MV-04",  # Felidhu Atoll
    "MV-05",  # Hahdhunmathi
    "MV-07",  # North Thiladhunmathi
    "MV-08",  # Kolhumadulu
    "MV-12",  # Mulaku Atoll
    "MV-13",  # North Maalhosmadulu
    "MV-14",  # North Nilandhe Atoll
    "MV-17",  # South Nilandhe Atoll
    "MV-20",  # South Maalhosmadulu
    "MV-23",  # South Thiladhunmathi
    "MV-24",  # North Miladhunmadulu
    "MV-25",  # South Miladhunmadulu
    "MV-26",  # Male Atoll
    "MV-27",  # North Huvadhu Atoll
    "MV-28",  # South Huvadhu Atoll
    "MV-29",  # Fuvammulah
    "MV-MLE",  # Male
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MVSubdivision(Subdivision):
    code: MVSubdivisionCodeType


MV: Final[Country] = Country(
    alpha2="MV",
    alpha3="MDV",
    name="Maldives",
    common_name=None,
    official_name="Republic of Maldives",
    subdivisions=[
        MVSubdivision(code="MV-00", name="South Ari Atoll", type_="Administrative atoll"),
        MVSubdivision(code="MV-01", name="Addu City", type_="City"),
        MVSubdivision(code="MV-02", name="North Ari Atoll", type_="Administrative atoll"),
        MVSubdivision(code="MV-03", name="Faadhippolhu", type_="Administrative atoll"),
        MVSubdivision(code="MV-04", name="Felidhu Atoll", type_="Administrative atoll"),
        MVSubdivision(code="MV-05", name="Hahdhunmathi", type_="Administrative atoll"),
        MVSubdivision(code="MV-07", name="North Thiladhunmathi", type_="Administrative atoll"),
        MVSubdivision(code="MV-08", name="Kolhumadulu", type_="Administrative atoll"),
        MVSubdivision(code="MV-12", name="Mulaku Atoll", type_="Administrative atoll"),
        MVSubdivision(code="MV-13", name="North Maalhosmadulu", type_="Administrative atoll"),
        MVSubdivision(code="MV-14", name="North Nilandhe Atoll", type_="Administrative atoll"),
        MVSubdivision(code="MV-17", name="South Nilandhe Atoll", type_="Administrative atoll"),
        MVSubdivision(code="MV-20", name="South Maalhosmadulu", type_="Administrative atoll"),
        MVSubdivision(code="MV-23", name="South Thiladhunmathi", type_="Administrative atoll"),
        MVSubdivision(code="MV-24", name="North Miladhunmadulu", type_="Administrative atoll"),
        MVSubdivision(code="MV-25", name="South Miladhunmadulu", type_="Administrative atoll"),
        MVSubdivision(code="MV-26", name="Male Atoll", type_="Administrative atoll"),
        MVSubdivision(code="MV-27", name="North Huvadhu Atoll", type_="Administrative atoll"),
        MVSubdivision(code="MV-28", name="South Huvadhu Atoll", type_="Administrative atoll"),
        MVSubdivision(code="MV-29", name="Fuvammulah", type_="Administrative atoll"),
        MVSubdivision(code="MV-MLE", name="Male", type_="City"),
    ],
)
