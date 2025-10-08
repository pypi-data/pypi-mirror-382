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

UASubdivisionCodeType = Literal[
    "UA-05",  # Vinnytska oblast
    "UA-07",  # Volynska oblast
    "UA-09",  # Luhanska oblast
    "UA-12",  # Dnipropetrovska oblast
    "UA-14",  # Donetska oblast
    "UA-18",  # Zhytomyrska oblast
    "UA-21",  # Zakarpatska oblast
    "UA-23",  # Zaporizka oblast
    "UA-26",  # Ivano-Frankivska oblast
    "UA-30",  # Kyiv
    "UA-32",  # Kyivska oblast
    "UA-35",  # Kirovohradska oblast
    "UA-40",  # Sevastopol
    "UA-43",  # Avtonomna Respublika Krym
    "UA-46",  # Lvivska oblast
    "UA-48",  # Mykolaivska oblast
    "UA-51",  # Odeska oblast
    "UA-53",  # Poltavska oblast
    "UA-56",  # Rivnenska oblast
    "UA-59",  # Sumska oblast
    "UA-61",  # Ternopilska oblast
    "UA-63",  # Kharkivska oblast
    "UA-65",  # Khersonska oblast
    "UA-68",  # Khmelnytska oblast
    "UA-71",  # Cherkaska oblast
    "UA-74",  # Chernihivska oblast
    "UA-77",  # Chernivetska oblast
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class UASubdivision(Subdivision):
    code: UASubdivisionCodeType


UA: Final[Country] = Country(
    alpha2="UA",
    alpha3="UKR",
    name="Ukraine",
    common_name=None,
    official_name=None,
    subdivisions=[
        UASubdivision(code="UA-05", name="Vinnytska oblast", type_="Region"),
        UASubdivision(code="UA-07", name="Volynska oblast", type_="Region"),
        UASubdivision(code="UA-09", name="Luhanska oblast", type_="Region"),
        UASubdivision(code="UA-12", name="Dnipropetrovska oblast", type_="Region"),
        UASubdivision(code="UA-14", name="Donetska oblast", type_="Region"),
        UASubdivision(code="UA-18", name="Zhytomyrska oblast", type_="Region"),
        UASubdivision(code="UA-21", name="Zakarpatska oblast", type_="Region"),
        UASubdivision(code="UA-23", name="Zaporizka oblast", type_="Region"),
        UASubdivision(code="UA-26", name="Ivano-Frankivska oblast", type_="Region"),
        UASubdivision(code="UA-30", name="Kyiv", type_="City"),
        UASubdivision(code="UA-32", name="Kyivska oblast", type_="Region"),
        UASubdivision(code="UA-35", name="Kirovohradska oblast", type_="Region"),
        UASubdivision(code="UA-40", name="Sevastopol", type_="City"),
        UASubdivision(code="UA-43", name="Avtonomna Respublika Krym", type_="Republic"),
        UASubdivision(code="UA-46", name="Lvivska oblast", type_="Region"),
        UASubdivision(code="UA-48", name="Mykolaivska oblast", type_="Region"),
        UASubdivision(code="UA-51", name="Odeska oblast", type_="Region"),
        UASubdivision(code="UA-53", name="Poltavska oblast", type_="Region"),
        UASubdivision(code="UA-56", name="Rivnenska oblast", type_="Region"),
        UASubdivision(code="UA-59", name="Sumska oblast", type_="Region"),
        UASubdivision(code="UA-61", name="Ternopilska oblast", type_="Region"),
        UASubdivision(code="UA-63", name="Kharkivska oblast", type_="Region"),
        UASubdivision(code="UA-65", name="Khersonska oblast", type_="Region"),
        UASubdivision(code="UA-68", name="Khmelnytska oblast", type_="Region"),
        UASubdivision(code="UA-71", name="Cherkaska oblast", type_="Region"),
        UASubdivision(code="UA-74", name="Chernihivska oblast", type_="Region"),
        UASubdivision(code="UA-77", name="Chernivetska oblast", type_="Region"),
    ],
)
