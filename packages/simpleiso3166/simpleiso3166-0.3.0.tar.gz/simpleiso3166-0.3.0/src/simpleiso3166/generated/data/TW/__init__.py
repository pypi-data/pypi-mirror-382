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

TWSubdivisionCodeType = Literal[
    "TW-CHA",  # Changhua
    "TW-CYI",  # Chiayi
    "TW-CYQ",  # Chiayi
    "TW-HSQ",  # Hsinchu
    "TW-HSZ",  # Hsinchu
    "TW-HUA",  # Hualien
    "TW-ILA",  # Yilan
    "TW-KEE",  # Keelung
    "TW-KHH",  # Kaohsiung
    "TW-KIN",  # Kinmen
    "TW-LIE",  # Lienchiang
    "TW-MIA",  # Miaoli
    "TW-NAN",  # Nantou
    "TW-NWT",  # New Taipei
    "TW-PEN",  # Penghu
    "TW-PIF",  # Pingtung
    "TW-TAO",  # Taoyuan
    "TW-TNN",  # Tainan
    "TW-TPE",  # Taipei
    "TW-TTT",  # Taitung
    "TW-TXG",  # Taichung
    "TW-YUN",  # Yunlin
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class TWSubdivision(Subdivision):
    code: TWSubdivisionCodeType


TW: Final[Country] = Country(
    alpha2="TW",
    alpha3="TWN",
    name="Taiwan, Province of China",
    common_name="Taiwan",
    official_name="Taiwan, Province of China",
    subdivisions=[
        TWSubdivision(code="TW-CHA", name="Changhua", type_="County"),
        TWSubdivision(code="TW-CYI", name="Chiayi", type_="City"),
        TWSubdivision(code="TW-CYQ", name="Chiayi", type_="County"),
        TWSubdivision(code="TW-HSQ", name="Hsinchu", type_="County"),
        TWSubdivision(code="TW-HSZ", name="Hsinchu", type_="City"),
        TWSubdivision(code="TW-HUA", name="Hualien", type_="County"),
        TWSubdivision(code="TW-ILA", name="Yilan", type_="County"),
        TWSubdivision(code="TW-KEE", name="Keelung", type_="City"),
        TWSubdivision(code="TW-KHH", name="Kaohsiung", type_="Special municipality"),
        TWSubdivision(code="TW-KIN", name="Kinmen", type_="County"),
        TWSubdivision(code="TW-LIE", name="Lienchiang", type_="County"),
        TWSubdivision(code="TW-MIA", name="Miaoli", type_="County"),
        TWSubdivision(code="TW-NAN", name="Nantou", type_="County"),
        TWSubdivision(code="TW-NWT", name="New Taipei", type_="Special municipality"),
        TWSubdivision(code="TW-PEN", name="Penghu", type_="County"),
        TWSubdivision(code="TW-PIF", name="Pingtung", type_="County"),
        TWSubdivision(code="TW-TAO", name="Taoyuan", type_="Special municipality"),
        TWSubdivision(code="TW-TNN", name="Tainan", type_="Special municipality"),
        TWSubdivision(code="TW-TPE", name="Taipei", type_="Special municipality"),
        TWSubdivision(code="TW-TTT", name="Taitung", type_="County"),
        TWSubdivision(code="TW-TXG", name="Taichung", type_="Special municipality"),
        TWSubdivision(code="TW-YUN", name="Yunlin", type_="County"),
    ],
)
