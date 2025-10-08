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

HRSubdivisionCodeType = Literal[
    "HR-01",  # Zagrebačka županija
    "HR-02",  # Krapinsko-zagorska županija
    "HR-03",  # Sisačko-moslavačka županija
    "HR-04",  # Karlovačka županija
    "HR-05",  # Varaždinska županija
    "HR-06",  # Koprivničko-križevačka županija
    "HR-07",  # Bjelovarsko-bilogorska županija
    "HR-08",  # Primorsko-goranska županija
    "HR-09",  # Ličko-senjska županija
    "HR-10",  # Virovitičko-podravska županija
    "HR-11",  # Požeško-slavonska županija
    "HR-12",  # Brodsko-posavska županija
    "HR-13",  # Zadarska županija
    "HR-14",  # Osječko-baranjska županija
    "HR-15",  # Šibensko-kninska županija
    "HR-16",  # Vukovarsko-srijemska županija
    "HR-17",  # Splitsko-dalmatinska županija
    "HR-18",  # Istarska županija
    "HR-19",  # Dubrovačko-neretvanska županija
    "HR-20",  # Međimurska županija
    "HR-21",  # Grad Zagreb
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class HRSubdivision(Subdivision):
    code: HRSubdivisionCodeType


HR: Final[Country] = Country(
    alpha2="HR",
    alpha3="HRV",
    name="Croatia",
    common_name=None,
    official_name="Republic of Croatia",
    subdivisions=[
        HRSubdivision(code="HR-01", name="Zagrebačka županija", type_="County"),
        HRSubdivision(code="HR-02", name="Krapinsko-zagorska županija", type_="County"),
        HRSubdivision(code="HR-03", name="Sisačko-moslavačka županija", type_="County"),
        HRSubdivision(code="HR-04", name="Karlovačka županija", type_="County"),
        HRSubdivision(code="HR-05", name="Varaždinska županija", type_="County"),
        HRSubdivision(code="HR-06", name="Koprivničko-križevačka županija", type_="County"),
        HRSubdivision(code="HR-07", name="Bjelovarsko-bilogorska županija", type_="County"),
        HRSubdivision(code="HR-08", name="Primorsko-goranska županija", type_="County"),
        HRSubdivision(code="HR-09", name="Ličko-senjska županija", type_="County"),
        HRSubdivision(code="HR-10", name="Virovitičko-podravska županija", type_="County"),
        HRSubdivision(code="HR-11", name="Požeško-slavonska županija", type_="County"),
        HRSubdivision(code="HR-12", name="Brodsko-posavska županija", type_="County"),
        HRSubdivision(code="HR-13", name="Zadarska županija", type_="County"),
        HRSubdivision(code="HR-14", name="Osječko-baranjska županija", type_="County"),
        HRSubdivision(code="HR-15", name="Šibensko-kninska županija", type_="County"),
        HRSubdivision(code="HR-16", name="Vukovarsko-srijemska županija", type_="County"),
        HRSubdivision(code="HR-17", name="Splitsko-dalmatinska županija", type_="County"),
        HRSubdivision(code="HR-18", name="Istarska županija", type_="County"),
        HRSubdivision(code="HR-19", name="Dubrovačko-neretvanska županija", type_="County"),
        HRSubdivision(code="HR-20", name="Međimurska županija", type_="County"),
        HRSubdivision(code="HR-21", name="Grad Zagreb", type_="City"),
    ],
)
