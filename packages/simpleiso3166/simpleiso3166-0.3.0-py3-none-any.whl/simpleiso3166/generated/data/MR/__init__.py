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

MRSubdivisionCodeType = Literal[
    "MR-01",  # Hodh ech Chargui
    "MR-02",  # Hodh el Gharbi
    "MR-03",  # Assaba
    "MR-04",  # Gorgol
    "MR-05",  # Brakna
    "MR-06",  # Trarza
    "MR-07",  # Adrar
    "MR-08",  # Dakhlet Nouâdhibou
    "MR-09",  # Tagant
    "MR-10",  # Guidimaka
    "MR-11",  # Tiris Zemmour
    "MR-12",  # Inchiri
    "MR-13",  # Nouakchott Ouest
    "MR-14",  # Nouakchott Nord
    "MR-15",  # Nouakchott Sud
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MRSubdivision(Subdivision):
    code: MRSubdivisionCodeType


MR: Final[Country] = Country(
    alpha2="MR",
    alpha3="MRT",
    name="Mauritania",
    common_name=None,
    official_name="Islamic Republic of Mauritania",
    subdivisions=[
        MRSubdivision(code="MR-01", name="Hodh ech Chargui", type_="Region"),
        MRSubdivision(code="MR-02", name="Hodh el Gharbi", type_="Region"),
        MRSubdivision(code="MR-03", name="Assaba", type_="Region"),
        MRSubdivision(code="MR-04", name="Gorgol", type_="Region"),
        MRSubdivision(code="MR-05", name="Brakna", type_="Region"),
        MRSubdivision(code="MR-06", name="Trarza", type_="Region"),
        MRSubdivision(code="MR-07", name="Adrar", type_="Region"),
        MRSubdivision(code="MR-08", name="Dakhlet Nouâdhibou", type_="Region"),
        MRSubdivision(code="MR-09", name="Tagant", type_="Region"),
        MRSubdivision(code="MR-10", name="Guidimaka", type_="Region"),
        MRSubdivision(code="MR-11", name="Tiris Zemmour", type_="Region"),
        MRSubdivision(code="MR-12", name="Inchiri", type_="Region"),
        MRSubdivision(code="MR-13", name="Nouakchott Ouest", type_="Region"),
        MRSubdivision(code="MR-14", name="Nouakchott Nord", type_="Region"),
        MRSubdivision(code="MR-15", name="Nouakchott Sud", type_="Region"),
    ],
)
