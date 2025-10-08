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

MDSubdivisionCodeType = Literal[
    "MD-AN",  # Anenii Noi
    "MD-BA",  # Bălți
    "MD-BD",  # Bender [Tighina]
    "MD-BR",  # Briceni
    "MD-BS",  # Basarabeasca
    "MD-CA",  # Cahul
    "MD-CL",  # Călărași
    "MD-CM",  # Cimișlia
    "MD-CR",  # Criuleni
    "MD-CS",  # Căușeni
    "MD-CT",  # Cantemir
    "MD-CU",  # Chișinău
    "MD-DO",  # Dondușeni
    "MD-DR",  # Drochia
    "MD-DU",  # Dubăsari
    "MD-ED",  # Edineț
    "MD-FA",  # Fălești
    "MD-FL",  # Florești
    "MD-GA",  # Găgăuzia, Unitatea teritorială autonomă (UTAG)
    "MD-GL",  # Glodeni
    "MD-HI",  # Hîncești
    "MD-IA",  # Ialoveni
    "MD-LE",  # Leova
    "MD-NI",  # Nisporeni
    "MD-OC",  # Ocnița
    "MD-OR",  # Orhei
    "MD-RE",  # Rezina
    "MD-RI",  # Rîșcani
    "MD-SD",  # Șoldănești
    "MD-SI",  # Sîngerei
    "MD-SN",  # Stînga Nistrului, unitatea teritorială din
    "MD-SO",  # Soroca
    "MD-ST",  # Strășeni
    "MD-SV",  # Ștefan Vodă
    "MD-TA",  # Taraclia
    "MD-TE",  # Telenești
    "MD-UN",  # Ungheni
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MDSubdivision(Subdivision):
    code: MDSubdivisionCodeType


MD: Final[Country] = Country(
    alpha2="MD",
    alpha3="MDA",
    name="Moldova, Republic of",
    common_name="Moldova",
    official_name="Republic of Moldova",
    subdivisions=[
        MDSubdivision(code="MD-AN", name="Anenii Noi", type_="District"),
        MDSubdivision(code="MD-BA", name="Bălți", type_="City"),
        MDSubdivision(code="MD-BD", name="Bender [Tighina]", type_="City"),
        MDSubdivision(code="MD-BR", name="Briceni", type_="District"),
        MDSubdivision(code="MD-BS", name="Basarabeasca", type_="District"),
        MDSubdivision(code="MD-CA", name="Cahul", type_="District"),
        MDSubdivision(code="MD-CL", name="Călărași", type_="District"),
        MDSubdivision(code="MD-CM", name="Cimișlia", type_="District"),
        MDSubdivision(code="MD-CR", name="Criuleni", type_="District"),
        MDSubdivision(code="MD-CS", name="Căușeni", type_="District"),
        MDSubdivision(code="MD-CT", name="Cantemir", type_="District"),
        MDSubdivision(code="MD-CU", name="Chișinău", type_="City"),
        MDSubdivision(code="MD-DO", name="Dondușeni", type_="District"),
        MDSubdivision(code="MD-DR", name="Drochia", type_="District"),
        MDSubdivision(code="MD-DU", name="Dubăsari", type_="District"),
        MDSubdivision(code="MD-ED", name="Edineț", type_="District"),
        MDSubdivision(code="MD-FA", name="Fălești", type_="District"),
        MDSubdivision(code="MD-FL", name="Florești", type_="District"),
        MDSubdivision(
            code="MD-GA",
            name="Găgăuzia, Unitatea teritorială autonomă (UTAG)",
            type_="Autonomous territorial unit",
        ),
        MDSubdivision(code="MD-GL", name="Glodeni", type_="District"),
        MDSubdivision(code="MD-HI", name="Hîncești", type_="District"),
        MDSubdivision(code="MD-IA", name="Ialoveni", type_="District"),
        MDSubdivision(code="MD-LE", name="Leova", type_="District"),
        MDSubdivision(code="MD-NI", name="Nisporeni", type_="District"),
        MDSubdivision(code="MD-OC", name="Ocnița", type_="District"),
        MDSubdivision(code="MD-OR", name="Orhei", type_="District"),
        MDSubdivision(code="MD-RE", name="Rezina", type_="District"),
        MDSubdivision(code="MD-RI", name="Rîșcani", type_="District"),
        MDSubdivision(code="MD-SD", name="Șoldănești", type_="District"),
        MDSubdivision(code="MD-SI", name="Sîngerei", type_="District"),
        MDSubdivision(code="MD-SN", name="Stînga Nistrului, unitatea teritorială din", type_="Territorial unit"),
        MDSubdivision(code="MD-SO", name="Soroca", type_="District"),
        MDSubdivision(code="MD-ST", name="Strășeni", type_="District"),
        MDSubdivision(code="MD-SV", name="Ștefan Vodă", type_="District"),
        MDSubdivision(code="MD-TA", name="Taraclia", type_="District"),
        MDSubdivision(code="MD-TE", name="Telenești", type_="District"),
        MDSubdivision(code="MD-UN", name="Ungheni", type_="District"),
    ],
)
