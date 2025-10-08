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

VNSubdivisionCodeType = Literal[
    "VN-01",  # Lai Châu
    "VN-02",  # Lào Cai
    "VN-03",  # Hà Giang
    "VN-04",  # Cao Bằng
    "VN-05",  # Sơn La
    "VN-06",  # Yên Bái
    "VN-07",  # Tuyên Quang
    "VN-09",  # Lạng Sơn
    "VN-13",  # Quảng Ninh
    "VN-14",  # Hòa Bình
    "VN-18",  # Ninh Bình
    "VN-20",  # Thái Bình
    "VN-21",  # Thanh Hóa
    "VN-22",  # Nghệ An
    "VN-23",  # Hà Tĩnh
    "VN-24",  # Quảng Bình
    "VN-25",  # Quảng Trị
    "VN-26",  # Thừa Thiên-Huế
    "VN-27",  # Quảng Nam
    "VN-28",  # Kon Tum
    "VN-29",  # Quảng Ngãi
    "VN-30",  # Gia Lai
    "VN-31",  # Bình Định
    "VN-32",  # Phú Yên
    "VN-33",  # Đắk Lắk
    "VN-34",  # Khánh Hòa
    "VN-35",  # Lâm Đồng
    "VN-36",  # Ninh Thuận
    "VN-37",  # Tây Ninh
    "VN-39",  # Đồng Nai
    "VN-40",  # Bình Thuận
    "VN-41",  # Long An
    "VN-43",  # Bà Rịa - Vũng Tàu
    "VN-44",  # An Giang
    "VN-45",  # Đồng Tháp
    "VN-46",  # Tiền Giang
    "VN-47",  # Kiến Giang
    "VN-49",  # Vĩnh Long
    "VN-50",  # Bến Tre
    "VN-51",  # Trà Vinh
    "VN-52",  # Sóc Trăng
    "VN-53",  # Bắc Kạn
    "VN-54",  # Bắc Giang
    "VN-55",  # Bạc Liêu
    "VN-56",  # Bắc Ninh
    "VN-57",  # Bình Dương
    "VN-58",  # Bình Phước
    "VN-59",  # Cà Mau
    "VN-61",  # Hải Dương
    "VN-63",  # Hà Nam
    "VN-66",  # Hưng Yên
    "VN-67",  # Nam Định
    "VN-68",  # Phú Thọ
    "VN-69",  # Thái Nguyên
    "VN-70",  # Vĩnh Phúc
    "VN-71",  # Điện Biên
    "VN-72",  # Đắk Nông
    "VN-73",  # Hậu Giang
    "VN-CT",  # Cần Thơ
    "VN-DN",  # Đà Nẵng
    "VN-HN",  # Hà Nội
    "VN-HP",  # Hải Phòng
    "VN-SG",  # Hồ Chí Minh
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class VNSubdivision(Subdivision):
    code: VNSubdivisionCodeType


VN: Final[Country] = Country(
    alpha2="VN",
    alpha3="VNM",
    name="Viet Nam",
    common_name="Vietnam",
    official_name="Socialist Republic of Viet Nam",
    subdivisions=[
        VNSubdivision(code="VN-01", name="Lai Châu", type_="Province"),
        VNSubdivision(code="VN-02", name="Lào Cai", type_="Province"),
        VNSubdivision(code="VN-03", name="Hà Giang", type_="Province"),
        VNSubdivision(code="VN-04", name="Cao Bằng", type_="Province"),
        VNSubdivision(code="VN-05", name="Sơn La", type_="Province"),
        VNSubdivision(code="VN-06", name="Yên Bái", type_="Province"),
        VNSubdivision(code="VN-07", name="Tuyên Quang", type_="Province"),
        VNSubdivision(code="VN-09", name="Lạng Sơn", type_="Province"),
        VNSubdivision(code="VN-13", name="Quảng Ninh", type_="Province"),
        VNSubdivision(code="VN-14", name="Hòa Bình", type_="Province"),
        VNSubdivision(code="VN-18", name="Ninh Bình", type_="Province"),
        VNSubdivision(code="VN-20", name="Thái Bình", type_="Province"),
        VNSubdivision(code="VN-21", name="Thanh Hóa", type_="Province"),
        VNSubdivision(code="VN-22", name="Nghệ An", type_="Province"),
        VNSubdivision(code="VN-23", name="Hà Tĩnh", type_="Province"),
        VNSubdivision(code="VN-24", name="Quảng Bình", type_="Province"),
        VNSubdivision(code="VN-25", name="Quảng Trị", type_="Province"),
        VNSubdivision(code="VN-26", name="Thừa Thiên-Huế", type_="Province"),
        VNSubdivision(code="VN-27", name="Quảng Nam", type_="Province"),
        VNSubdivision(code="VN-28", name="Kon Tum", type_="Province"),
        VNSubdivision(code="VN-29", name="Quảng Ngãi", type_="Province"),
        VNSubdivision(code="VN-30", name="Gia Lai", type_="Province"),
        VNSubdivision(code="VN-31", name="Bình Định", type_="Province"),
        VNSubdivision(code="VN-32", name="Phú Yên", type_="Province"),
        VNSubdivision(code="VN-33", name="Đắk Lắk", type_="Province"),
        VNSubdivision(code="VN-34", name="Khánh Hòa", type_="Province"),
        VNSubdivision(code="VN-35", name="Lâm Đồng", type_="Province"),
        VNSubdivision(code="VN-36", name="Ninh Thuận", type_="Province"),
        VNSubdivision(code="VN-37", name="Tây Ninh", type_="Province"),
        VNSubdivision(code="VN-39", name="Đồng Nai", type_="Province"),
        VNSubdivision(code="VN-40", name="Bình Thuận", type_="Province"),
        VNSubdivision(code="VN-41", name="Long An", type_="Province"),
        VNSubdivision(code="VN-43", name="Bà Rịa - Vũng Tàu", type_="Province"),
        VNSubdivision(code="VN-44", name="An Giang", type_="Province"),
        VNSubdivision(code="VN-45", name="Đồng Tháp", type_="Province"),
        VNSubdivision(code="VN-46", name="Tiền Giang", type_="Province"),
        VNSubdivision(code="VN-47", name="Kiến Giang", type_="Province"),
        VNSubdivision(code="VN-49", name="Vĩnh Long", type_="Province"),
        VNSubdivision(code="VN-50", name="Bến Tre", type_="Province"),
        VNSubdivision(code="VN-51", name="Trà Vinh", type_="Province"),
        VNSubdivision(code="VN-52", name="Sóc Trăng", type_="Province"),
        VNSubdivision(code="VN-53", name="Bắc Kạn", type_="Province"),
        VNSubdivision(code="VN-54", name="Bắc Giang", type_="Province"),
        VNSubdivision(code="VN-55", name="Bạc Liêu", type_="Province"),
        VNSubdivision(code="VN-56", name="Bắc Ninh", type_="Province"),
        VNSubdivision(code="VN-57", name="Bình Dương", type_="Province"),
        VNSubdivision(code="VN-58", name="Bình Phước", type_="Province"),
        VNSubdivision(code="VN-59", name="Cà Mau", type_="Province"),
        VNSubdivision(code="VN-61", name="Hải Dương", type_="Province"),
        VNSubdivision(code="VN-63", name="Hà Nam", type_="Province"),
        VNSubdivision(code="VN-66", name="Hưng Yên", type_="Province"),
        VNSubdivision(code="VN-67", name="Nam Định", type_="Province"),
        VNSubdivision(code="VN-68", name="Phú Thọ", type_="Province"),
        VNSubdivision(code="VN-69", name="Thái Nguyên", type_="Province"),
        VNSubdivision(code="VN-70", name="Vĩnh Phúc", type_="Province"),
        VNSubdivision(code="VN-71", name="Điện Biên", type_="Province"),
        VNSubdivision(code="VN-72", name="Đắk Nông", type_="Province"),
        VNSubdivision(code="VN-73", name="Hậu Giang", type_="Province"),
        VNSubdivision(code="VN-CT", name="Cần Thơ", type_="Municipality"),
        VNSubdivision(code="VN-DN", name="Đà Nẵng", type_="Municipality"),
        VNSubdivision(code="VN-HN", name="Hà Nội", type_="Municipality"),
        VNSubdivision(code="VN-HP", name="Hải Phòng", type_="Municipality"),
        VNSubdivision(code="VN-SG", name="Hồ Chí Minh", type_="Municipality"),
    ],
)
