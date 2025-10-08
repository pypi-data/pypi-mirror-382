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

CNSubdivisionCodeType = Literal[
    "CN-AH",  # Anhui Sheng
    "CN-BJ",  # Beijing Shi
    "CN-CQ",  # Chongqing Shi
    "CN-FJ",  # Fujian Sheng
    "CN-GD",  # Guangdong Sheng
    "CN-GS",  # Gansu Sheng
    "CN-GX",  # Guangxi Zhuangzu Zizhiqu
    "CN-GZ",  # Guizhou Sheng
    "CN-HA",  # Henan Sheng
    "CN-HB",  # Hubei Sheng
    "CN-HE",  # Hebei Sheng
    "CN-HI",  # Hainan Sheng
    "CN-HK",  # Hong Kong SAR
    "CN-HL",  # Heilongjiang Sheng
    "CN-HN",  # Hunan Sheng
    "CN-JL",  # Jilin Sheng
    "CN-JS",  # Jiangsu Sheng
    "CN-JX",  # Jiangxi Sheng
    "CN-LN",  # Liaoning Sheng
    "CN-MO",  # Macao SAR
    "CN-NM",  # Nei Mongol Zizhiqu
    "CN-NX",  # Ningxia Huizu Zizhiqu
    "CN-QH",  # Qinghai Sheng
    "CN-SC",  # Sichuan Sheng
    "CN-SD",  # Shandong Sheng
    "CN-SH",  # Shanghai Shi
    "CN-SN",  # Shaanxi Sheng
    "CN-SX",  # Shanxi Sheng
    "CN-TJ",  # Tianjin Shi
    "CN-TW",  # Taiwan Sheng
    "CN-XJ",  # Xinjiang Uygur Zizhiqu
    "CN-XZ",  # Xizang Zizhiqu
    "CN-YN",  # Yunnan Sheng
    "CN-ZJ",  # Zhejiang Sheng
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class CNSubdivision(Subdivision):
    code: CNSubdivisionCodeType


CN: Final[Country] = Country(
    alpha2="CN",
    alpha3="CHN",
    name="China",
    common_name=None,
    official_name="People's Republic of China",
    subdivisions=[
        CNSubdivision(code="CN-AH", name="Anhui Sheng", type_="Province"),
        CNSubdivision(code="CN-BJ", name="Beijing Shi", type_="Municipality"),
        CNSubdivision(code="CN-CQ", name="Chongqing Shi", type_="Municipality"),
        CNSubdivision(code="CN-FJ", name="Fujian Sheng", type_="Province"),
        CNSubdivision(code="CN-GD", name="Guangdong Sheng", type_="Province"),
        CNSubdivision(code="CN-GS", name="Gansu Sheng", type_="Province"),
        CNSubdivision(code="CN-GX", name="Guangxi Zhuangzu Zizhiqu", type_="Autonomous region"),
        CNSubdivision(code="CN-GZ", name="Guizhou Sheng", type_="Province"),
        CNSubdivision(code="CN-HA", name="Henan Sheng", type_="Province"),
        CNSubdivision(code="CN-HB", name="Hubei Sheng", type_="Province"),
        CNSubdivision(code="CN-HE", name="Hebei Sheng", type_="Province"),
        CNSubdivision(code="CN-HI", name="Hainan Sheng", type_="Province"),
        CNSubdivision(code="CN-HK", name="Hong Kong SAR", type_="Special administrative region"),
        CNSubdivision(code="CN-HL", name="Heilongjiang Sheng", type_="Province"),
        CNSubdivision(code="CN-HN", name="Hunan Sheng", type_="Province"),
        CNSubdivision(code="CN-JL", name="Jilin Sheng", type_="Province"),
        CNSubdivision(code="CN-JS", name="Jiangsu Sheng", type_="Province"),
        CNSubdivision(code="CN-JX", name="Jiangxi Sheng", type_="Province"),
        CNSubdivision(code="CN-LN", name="Liaoning Sheng", type_="Province"),
        CNSubdivision(code="CN-MO", name="Macao SAR", type_="Special administrative region"),
        CNSubdivision(code="CN-NM", name="Nei Mongol Zizhiqu", type_="Autonomous region"),
        CNSubdivision(code="CN-NX", name="Ningxia Huizu Zizhiqu", type_="Autonomous region"),
        CNSubdivision(code="CN-QH", name="Qinghai Sheng", type_="Province"),
        CNSubdivision(code="CN-SC", name="Sichuan Sheng", type_="Province"),
        CNSubdivision(code="CN-SD", name="Shandong Sheng", type_="Province"),
        CNSubdivision(code="CN-SH", name="Shanghai Shi", type_="Municipality"),
        CNSubdivision(code="CN-SN", name="Shaanxi Sheng", type_="Province"),
        CNSubdivision(code="CN-SX", name="Shanxi Sheng", type_="Province"),
        CNSubdivision(code="CN-TJ", name="Tianjin Shi", type_="Municipality"),
        CNSubdivision(code="CN-TW", name="Taiwan Sheng", type_="Province"),
        CNSubdivision(code="CN-XJ", name="Xinjiang Uygur Zizhiqu", type_="Autonomous region"),
        CNSubdivision(code="CN-XZ", name="Xizang Zizhiqu", type_="Autonomous region"),
        CNSubdivision(code="CN-YN", name="Yunnan Sheng", type_="Province"),
        CNSubdivision(code="CN-ZJ", name="Zhejiang Sheng", type_="Province"),
    ],
)
