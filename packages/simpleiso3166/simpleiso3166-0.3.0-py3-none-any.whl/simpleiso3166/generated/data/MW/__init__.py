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

MWSubdivisionCodeType = Literal[
    "MW-BA",  # Balaka
    "MW-BL",  # Blantyre
    "MW-C",  # Central Region
    "MW-CK",  # Chikwawa
    "MW-CR",  # Chiradzulu
    "MW-CT",  # Chitipa
    "MW-DE",  # Dedza
    "MW-DO",  # Dowa
    "MW-KR",  # Karonga
    "MW-KS",  # Kasungu
    "MW-LI",  # Lilongwe
    "MW-LK",  # Likoma
    "MW-MC",  # Mchinji
    "MW-MG",  # Mangochi
    "MW-MH",  # Machinga
    "MW-MU",  # Mulanje
    "MW-MW",  # Mwanza
    "MW-MZ",  # Mzimba
    "MW-N",  # Northern Region
    "MW-NB",  # Nkhata Bay
    "MW-NE",  # Neno
    "MW-NI",  # Ntchisi
    "MW-NK",  # Nkhotakota
    "MW-NS",  # Nsanje
    "MW-NU",  # Ntcheu
    "MW-PH",  # Phalombe
    "MW-RU",  # Rumphi
    "MW-S",  # Southern Region
    "MW-SA",  # Salima
    "MW-TH",  # Thyolo
    "MW-ZO",  # Zomba
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MWSubdivision(Subdivision):
    code: MWSubdivisionCodeType


MW: Final[Country] = Country(
    alpha2="MW",
    alpha3="MWI",
    name="Malawi",
    common_name=None,
    official_name="Republic of Malawi",
    subdivisions=[
        MWSubdivision(code="MW-BA", name="Balaka", type_="District"),
        MWSubdivision(code="MW-BL", name="Blantyre", type_="District"),
        MWSubdivision(code="MW-C", name="Central Region", type_="Region"),
        MWSubdivision(code="MW-CK", name="Chikwawa", type_="District"),
        MWSubdivision(code="MW-CR", name="Chiradzulu", type_="District"),
        MWSubdivision(code="MW-CT", name="Chitipa", type_="District"),
        MWSubdivision(code="MW-DE", name="Dedza", type_="District"),
        MWSubdivision(code="MW-DO", name="Dowa", type_="District"),
        MWSubdivision(code="MW-KR", name="Karonga", type_="District"),
        MWSubdivision(code="MW-KS", name="Kasungu", type_="District"),
        MWSubdivision(code="MW-LI", name="Lilongwe", type_="District"),
        MWSubdivision(code="MW-LK", name="Likoma", type_="District"),
        MWSubdivision(code="MW-MC", name="Mchinji", type_="District"),
        MWSubdivision(code="MW-MG", name="Mangochi", type_="District"),
        MWSubdivision(code="MW-MH", name="Machinga", type_="District"),
        MWSubdivision(code="MW-MU", name="Mulanje", type_="District"),
        MWSubdivision(code="MW-MW", name="Mwanza", type_="District"),
        MWSubdivision(code="MW-MZ", name="Mzimba", type_="District"),
        MWSubdivision(code="MW-N", name="Northern Region", type_="Region"),
        MWSubdivision(code="MW-NB", name="Nkhata Bay", type_="District"),
        MWSubdivision(code="MW-NE", name="Neno", type_="District"),
        MWSubdivision(code="MW-NI", name="Ntchisi", type_="District"),
        MWSubdivision(code="MW-NK", name="Nkhotakota", type_="District"),
        MWSubdivision(code="MW-NS", name="Nsanje", type_="District"),
        MWSubdivision(code="MW-NU", name="Ntcheu", type_="District"),
        MWSubdivision(code="MW-PH", name="Phalombe", type_="District"),
        MWSubdivision(code="MW-RU", name="Rumphi", type_="District"),
        MWSubdivision(code="MW-S", name="Southern Region", type_="Region"),
        MWSubdivision(code="MW-SA", name="Salima", type_="District"),
        MWSubdivision(code="MW-TH", name="Thyolo", type_="District"),
        MWSubdivision(code="MW-ZO", name="Zomba", type_="District"),
    ],
)
