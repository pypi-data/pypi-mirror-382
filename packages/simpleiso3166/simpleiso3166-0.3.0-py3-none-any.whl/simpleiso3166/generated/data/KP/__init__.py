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

KPSubdivisionCodeType = Literal[
    "KP-01",  # P'yǒngyang
    "KP-02",  # P'yǒngan-namdo
    "KP-03",  # P'yǒngan-bukto
    "KP-04",  # Chagang-do
    "KP-05",  # Hwanghae-namdo
    "KP-06",  # Hwanghae-bukto
    "KP-07",  # Kangweonto
    "KP-08",  # Hamgyǒng-namdo
    "KP-09",  # Hamgyǒng-bukto
    "KP-10",  # Ryanggang-do
    "KP-13",  # Raseon
    "KP-14",  # Nampho
    "KP-15",  # Kaeseong
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class KPSubdivision(Subdivision):
    code: KPSubdivisionCodeType


KP: Final[Country] = Country(
    alpha2="KP",
    alpha3="PRK",
    name="Korea, Democratic People's Republic of",
    common_name="North Korea",
    official_name="Democratic People's Republic of Korea",
    subdivisions=[
        KPSubdivision(code="KP-01", name="P'yǒngyang", type_="Capital city"),
        KPSubdivision(code="KP-02", name="P'yǒngan-namdo", type_="Province"),
        KPSubdivision(code="KP-03", name="P'yǒngan-bukto", type_="Province"),
        KPSubdivision(code="KP-04", name="Chagang-do", type_="Province"),
        KPSubdivision(code="KP-05", name="Hwanghae-namdo", type_="Province"),
        KPSubdivision(code="KP-06", name="Hwanghae-bukto", type_="Province"),
        KPSubdivision(code="KP-07", name="Kangweonto", type_="Province"),
        KPSubdivision(code="KP-08", name="Hamgyǒng-namdo", type_="Province"),
        KPSubdivision(code="KP-09", name="Hamgyǒng-bukto", type_="Province"),
        KPSubdivision(code="KP-10", name="Ryanggang-do", type_="Province"),
        KPSubdivision(code="KP-13", name="Raseon", type_="Special city"),
        KPSubdivision(code="KP-14", name="Nampho", type_="Metropolitan city"),
        KPSubdivision(code="KP-15", name="Kaeseong", type_="Metropolitan city"),
    ],
)
