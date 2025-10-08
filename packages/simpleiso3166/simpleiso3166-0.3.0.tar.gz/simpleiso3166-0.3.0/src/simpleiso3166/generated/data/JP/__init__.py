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

JPSubdivisionCodeType = Literal[
    "JP-01",  # Hokkaido
    "JP-02",  # Aomori
    "JP-03",  # Iwate
    "JP-04",  # Miyagi
    "JP-05",  # Akita
    "JP-06",  # Yamagata
    "JP-07",  # Fukushima
    "JP-08",  # Ibaraki
    "JP-09",  # Tochigi
    "JP-10",  # Gunma
    "JP-11",  # Saitama
    "JP-12",  # Chiba
    "JP-13",  # Tokyo
    "JP-14",  # Kanagawa
    "JP-15",  # Niigata
    "JP-16",  # Toyama
    "JP-17",  # Ishikawa
    "JP-18",  # Fukui
    "JP-19",  # Yamanashi
    "JP-20",  # Nagano
    "JP-21",  # Gifu
    "JP-22",  # Shizuoka
    "JP-23",  # Aichi
    "JP-24",  # Mie
    "JP-25",  # Shiga
    "JP-26",  # Kyoto
    "JP-27",  # Osaka
    "JP-28",  # Hyogo
    "JP-29",  # Nara
    "JP-30",  # Wakayama
    "JP-31",  # Tottori
    "JP-32",  # Shimane
    "JP-33",  # Okayama
    "JP-34",  # Hiroshima
    "JP-35",  # Yamaguchi
    "JP-36",  # Tokushima
    "JP-37",  # Kagawa
    "JP-38",  # Ehime
    "JP-39",  # Kochi
    "JP-40",  # Fukuoka
    "JP-41",  # Saga
    "JP-42",  # Nagasaki
    "JP-43",  # Kumamoto
    "JP-44",  # Oita
    "JP-45",  # Miyazaki
    "JP-46",  # Kagoshima
    "JP-47",  # Okinawa
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class JPSubdivision(Subdivision):
    code: JPSubdivisionCodeType


JP: Final[Country] = Country(
    alpha2="JP",
    alpha3="JPN",
    name="Japan",
    common_name=None,
    official_name=None,
    subdivisions=[
        JPSubdivision(code="JP-01", name="Hokkaido", type_="Prefecture"),
        JPSubdivision(code="JP-02", name="Aomori", type_="Prefecture"),
        JPSubdivision(code="JP-03", name="Iwate", type_="Prefecture"),
        JPSubdivision(code="JP-04", name="Miyagi", type_="Prefecture"),
        JPSubdivision(code="JP-05", name="Akita", type_="Prefecture"),
        JPSubdivision(code="JP-06", name="Yamagata", type_="Prefecture"),
        JPSubdivision(code="JP-07", name="Fukushima", type_="Prefecture"),
        JPSubdivision(code="JP-08", name="Ibaraki", type_="Prefecture"),
        JPSubdivision(code="JP-09", name="Tochigi", type_="Prefecture"),
        JPSubdivision(code="JP-10", name="Gunma", type_="Prefecture"),
        JPSubdivision(code="JP-11", name="Saitama", type_="Prefecture"),
        JPSubdivision(code="JP-12", name="Chiba", type_="Prefecture"),
        JPSubdivision(code="JP-13", name="Tokyo", type_="Prefecture"),
        JPSubdivision(code="JP-14", name="Kanagawa", type_="Prefecture"),
        JPSubdivision(code="JP-15", name="Niigata", type_="Prefecture"),
        JPSubdivision(code="JP-16", name="Toyama", type_="Prefecture"),
        JPSubdivision(code="JP-17", name="Ishikawa", type_="Prefecture"),
        JPSubdivision(code="JP-18", name="Fukui", type_="Prefecture"),
        JPSubdivision(code="JP-19", name="Yamanashi", type_="Prefecture"),
        JPSubdivision(code="JP-20", name="Nagano", type_="Prefecture"),
        JPSubdivision(code="JP-21", name="Gifu", type_="Prefecture"),
        JPSubdivision(code="JP-22", name="Shizuoka", type_="Prefecture"),
        JPSubdivision(code="JP-23", name="Aichi", type_="Prefecture"),
        JPSubdivision(code="JP-24", name="Mie", type_="Prefecture"),
        JPSubdivision(code="JP-25", name="Shiga", type_="Prefecture"),
        JPSubdivision(code="JP-26", name="Kyoto", type_="Prefecture"),
        JPSubdivision(code="JP-27", name="Osaka", type_="Prefecture"),
        JPSubdivision(code="JP-28", name="Hyogo", type_="Prefecture"),
        JPSubdivision(code="JP-29", name="Nara", type_="Prefecture"),
        JPSubdivision(code="JP-30", name="Wakayama", type_="Prefecture"),
        JPSubdivision(code="JP-31", name="Tottori", type_="Prefecture"),
        JPSubdivision(code="JP-32", name="Shimane", type_="Prefecture"),
        JPSubdivision(code="JP-33", name="Okayama", type_="Prefecture"),
        JPSubdivision(code="JP-34", name="Hiroshima", type_="Prefecture"),
        JPSubdivision(code="JP-35", name="Yamaguchi", type_="Prefecture"),
        JPSubdivision(code="JP-36", name="Tokushima", type_="Prefecture"),
        JPSubdivision(code="JP-37", name="Kagawa", type_="Prefecture"),
        JPSubdivision(code="JP-38", name="Ehime", type_="Prefecture"),
        JPSubdivision(code="JP-39", name="Kochi", type_="Prefecture"),
        JPSubdivision(code="JP-40", name="Fukuoka", type_="Prefecture"),
        JPSubdivision(code="JP-41", name="Saga", type_="Prefecture"),
        JPSubdivision(code="JP-42", name="Nagasaki", type_="Prefecture"),
        JPSubdivision(code="JP-43", name="Kumamoto", type_="Prefecture"),
        JPSubdivision(code="JP-44", name="Oita", type_="Prefecture"),
        JPSubdivision(code="JP-45", name="Miyazaki", type_="Prefecture"),
        JPSubdivision(code="JP-46", name="Kagoshima", type_="Prefecture"),
        JPSubdivision(code="JP-47", name="Okinawa", type_="Prefecture"),
    ],
)
