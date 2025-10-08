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

SASubdivisionCodeType = Literal[
    "SA-01",  # Ar Riyāḑ
    "SA-02",  # Makkah al Mukarramah
    "SA-03",  # Al Madīnah al Munawwarah
    "SA-04",  # Ash Sharqīyah
    "SA-05",  # Al Qaşīm
    "SA-06",  # Ḩā'il
    "SA-07",  # Tabūk
    "SA-08",  # Al Ḩudūd ash Shamālīyah
    "SA-09",  # Jāzān
    "SA-10",  # Najrān
    "SA-11",  # Al Bāḩah
    "SA-12",  # Al Jawf
    "SA-14",  # 'Asīr
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SASubdivision(Subdivision):
    code: SASubdivisionCodeType


SA: Final[Country] = Country(
    alpha2="SA",
    alpha3="SAU",
    name="Saudi Arabia",
    common_name=None,
    official_name="Kingdom of Saudi Arabia",
    subdivisions=[
        SASubdivision(code="SA-01", name="Ar Riyāḑ", type_="Region"),
        SASubdivision(code="SA-02", name="Makkah al Mukarramah", type_="Region"),
        SASubdivision(code="SA-03", name="Al Madīnah al Munawwarah", type_="Region"),
        SASubdivision(code="SA-04", name="Ash Sharqīyah", type_="Region"),
        SASubdivision(code="SA-05", name="Al Qaşīm", type_="Region"),
        SASubdivision(code="SA-06", name="Ḩā'il", type_="Region"),
        SASubdivision(code="SA-07", name="Tabūk", type_="Region"),
        SASubdivision(code="SA-08", name="Al Ḩudūd ash Shamālīyah", type_="Region"),
        SASubdivision(code="SA-09", name="Jāzān", type_="Region"),
        SASubdivision(code="SA-10", name="Najrān", type_="Region"),
        SASubdivision(code="SA-11", name="Al Bāḩah", type_="Region"),
        SASubdivision(code="SA-12", name="Al Jawf", type_="Region"),
        SASubdivision(code="SA-14", name="'Asīr", type_="Region"),
    ],
)
