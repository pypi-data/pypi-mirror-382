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

KRSubdivisionCodeType = Literal[
    "KR-11",  # Seoul-teukbyeolsi
    "KR-26",  # Busan-gwangyeoksi
    "KR-27",  # Daegu-gwangyeoksi
    "KR-28",  # Incheon-gwangyeoksi
    "KR-29",  # Gwangju-gwangyeoksi
    "KR-30",  # Daejeon-gwangyeoksi
    "KR-31",  # Ulsan-gwangyeoksi
    "KR-41",  # Gyeonggi-do
    "KR-42",  # Gangwon-teukbyeoljachido
    "KR-43",  # Chungcheongbuk-do
    "KR-44",  # Chungcheongnam-do
    "KR-45",  # Jeollabuk-do
    "KR-46",  # Jeollanam-do
    "KR-47",  # Gyeongsangbuk-do
    "KR-48",  # Gyeongsangnam-do
    "KR-49",  # Jeju-teukbyeoljachido
    "KR-50",  # Sejong
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class KRSubdivision(Subdivision):
    code: KRSubdivisionCodeType


KR: Final[Country] = Country(
    alpha2="KR",
    alpha3="KOR",
    name="Korea, Republic of",
    common_name="South Korea",
    official_name=None,
    subdivisions=[
        KRSubdivision(code="KR-11", name="Seoul-teukbyeolsi", type_="Special city"),
        KRSubdivision(code="KR-26", name="Busan-gwangyeoksi", type_="Metropolitan city"),
        KRSubdivision(code="KR-27", name="Daegu-gwangyeoksi", type_="Metropolitan city"),
        KRSubdivision(code="KR-28", name="Incheon-gwangyeoksi", type_="Metropolitan city"),
        KRSubdivision(code="KR-29", name="Gwangju-gwangyeoksi", type_="Metropolitan city"),
        KRSubdivision(code="KR-30", name="Daejeon-gwangyeoksi", type_="Metropolitan city"),
        KRSubdivision(code="KR-31", name="Ulsan-gwangyeoksi", type_="Metropolitan city"),
        KRSubdivision(code="KR-41", name="Gyeonggi-do", type_="Province"),
        KRSubdivision(code="KR-42", name="Gangwon-teukbyeoljachido", type_="Special self-governing province"),
        KRSubdivision(code="KR-43", name="Chungcheongbuk-do", type_="Province"),
        KRSubdivision(code="KR-44", name="Chungcheongnam-do", type_="Province"),
        KRSubdivision(code="KR-45", name="Jeollabuk-do", type_="Province"),
        KRSubdivision(code="KR-46", name="Jeollanam-do", type_="Province"),
        KRSubdivision(code="KR-47", name="Gyeongsangbuk-do", type_="Province"),
        KRSubdivision(code="KR-48", name="Gyeongsangnam-do", type_="Province"),
        KRSubdivision(code="KR-49", name="Jeju-teukbyeoljachido", type_="Special self-governing province"),
        KRSubdivision(code="KR-50", name="Sejong", type_="Special self-governing city"),
    ],
)
