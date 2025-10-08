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

NGSubdivisionCodeType = Literal[
    "NG-AB",  # Abia
    "NG-AD",  # Adamawa
    "NG-AK",  # Akwa Ibom
    "NG-AN",  # Anambra
    "NG-BA",  # Bauchi
    "NG-BE",  # Benue
    "NG-BO",  # Borno
    "NG-BY",  # Bayelsa
    "NG-CR",  # Cross River
    "NG-DE",  # Delta
    "NG-EB",  # Ebonyi
    "NG-ED",  # Edo
    "NG-EK",  # Ekiti
    "NG-EN",  # Enugu
    "NG-FC",  # Abuja Federal Capital Territory
    "NG-GO",  # Gombe
    "NG-IM",  # Imo
    "NG-JI",  # Jigawa
    "NG-KD",  # Kaduna
    "NG-KE",  # Kebbi
    "NG-KN",  # Kano
    "NG-KO",  # Kogi
    "NG-KT",  # Katsina
    "NG-KW",  # Kwara
    "NG-LA",  # Lagos
    "NG-NA",  # Nasarawa
    "NG-NI",  # Niger
    "NG-OG",  # Ogun
    "NG-ON",  # Ondo
    "NG-OS",  # Osun
    "NG-OY",  # Oyo
    "NG-PL",  # Plateau
    "NG-RI",  # Rivers
    "NG-SO",  # Sokoto
    "NG-TA",  # Taraba
    "NG-YO",  # Yobe
    "NG-ZA",  # Zamfara
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class NGSubdivision(Subdivision):
    code: NGSubdivisionCodeType


NG: Final[Country] = Country(
    alpha2="NG",
    alpha3="NGA",
    name="Nigeria",
    common_name=None,
    official_name="Federal Republic of Nigeria",
    subdivisions=[
        NGSubdivision(code="NG-AB", name="Abia", type_="State"),
        NGSubdivision(code="NG-AD", name="Adamawa", type_="State"),
        NGSubdivision(code="NG-AK", name="Akwa Ibom", type_="State"),
        NGSubdivision(code="NG-AN", name="Anambra", type_="State"),
        NGSubdivision(code="NG-BA", name="Bauchi", type_="State"),
        NGSubdivision(code="NG-BE", name="Benue", type_="State"),
        NGSubdivision(code="NG-BO", name="Borno", type_="State"),
        NGSubdivision(code="NG-BY", name="Bayelsa", type_="State"),
        NGSubdivision(code="NG-CR", name="Cross River", type_="State"),
        NGSubdivision(code="NG-DE", name="Delta", type_="State"),
        NGSubdivision(code="NG-EB", name="Ebonyi", type_="State"),
        NGSubdivision(code="NG-ED", name="Edo", type_="State"),
        NGSubdivision(code="NG-EK", name="Ekiti", type_="State"),
        NGSubdivision(code="NG-EN", name="Enugu", type_="State"),
        NGSubdivision(code="NG-FC", name="Abuja Federal Capital Territory", type_="Capital territory"),
        NGSubdivision(code="NG-GO", name="Gombe", type_="State"),
        NGSubdivision(code="NG-IM", name="Imo", type_="State"),
        NGSubdivision(code="NG-JI", name="Jigawa", type_="State"),
        NGSubdivision(code="NG-KD", name="Kaduna", type_="State"),
        NGSubdivision(code="NG-KE", name="Kebbi", type_="State"),
        NGSubdivision(code="NG-KN", name="Kano", type_="State"),
        NGSubdivision(code="NG-KO", name="Kogi", type_="State"),
        NGSubdivision(code="NG-KT", name="Katsina", type_="State"),
        NGSubdivision(code="NG-KW", name="Kwara", type_="State"),
        NGSubdivision(code="NG-LA", name="Lagos", type_="State"),
        NGSubdivision(code="NG-NA", name="Nasarawa", type_="State"),
        NGSubdivision(code="NG-NI", name="Niger", type_="State"),
        NGSubdivision(code="NG-OG", name="Ogun", type_="State"),
        NGSubdivision(code="NG-ON", name="Ondo", type_="State"),
        NGSubdivision(code="NG-OS", name="Osun", type_="State"),
        NGSubdivision(code="NG-OY", name="Oyo", type_="State"),
        NGSubdivision(code="NG-PL", name="Plateau", type_="State"),
        NGSubdivision(code="NG-RI", name="Rivers", type_="State"),
        NGSubdivision(code="NG-SO", name="Sokoto", type_="State"),
        NGSubdivision(code="NG-TA", name="Taraba", type_="State"),
        NGSubdivision(code="NG-YO", name="Yobe", type_="State"),
        NGSubdivision(code="NG-ZA", name="Zamfara", type_="State"),
    ],
)
