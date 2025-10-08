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

KESubdivisionCodeType = Literal[
    "KE-01",  # Baringo
    "KE-02",  # Bomet
    "KE-03",  # Bungoma
    "KE-04",  # Busia
    "KE-05",  # Elgeyo/Marakwet
    "KE-06",  # Embu
    "KE-07",  # Garissa
    "KE-08",  # Homa Bay
    "KE-09",  # Isiolo
    "KE-10",  # Kajiado
    "KE-11",  # Kakamega
    "KE-12",  # Kericho
    "KE-13",  # Kiambu
    "KE-14",  # Kilifi
    "KE-15",  # Kirinyaga
    "KE-16",  # Kisii
    "KE-17",  # Kisumu
    "KE-18",  # Kitui
    "KE-19",  # Kwale
    "KE-20",  # Laikipia
    "KE-21",  # Lamu
    "KE-22",  # Machakos
    "KE-23",  # Makueni
    "KE-24",  # Mandera
    "KE-25",  # Marsabit
    "KE-26",  # Meru
    "KE-27",  # Migori
    "KE-28",  # Mombasa
    "KE-29",  # Murang'a
    "KE-30",  # Nairobi City
    "KE-31",  # Nakuru
    "KE-32",  # Nandi
    "KE-33",  # Narok
    "KE-34",  # Nyamira
    "KE-35",  # Nyandarua
    "KE-36",  # Nyeri
    "KE-37",  # Samburu
    "KE-38",  # Siaya
    "KE-39",  # Taita/Taveta
    "KE-40",  # Tana River
    "KE-41",  # Tharaka-Nithi
    "KE-42",  # Trans Nzoia
    "KE-43",  # Turkana
    "KE-44",  # Uasin Gishu
    "KE-45",  # Vihiga
    "KE-46",  # Wajir
    "KE-47",  # West Pokot
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class KESubdivision(Subdivision):
    code: KESubdivisionCodeType


KE: Final[Country] = Country(
    alpha2="KE",
    alpha3="KEN",
    name="Kenya",
    common_name=None,
    official_name="Republic of Kenya",
    subdivisions=[
        KESubdivision(code="KE-01", name="Baringo", type_="County"),
        KESubdivision(code="KE-02", name="Bomet", type_="County"),
        KESubdivision(code="KE-03", name="Bungoma", type_="County"),
        KESubdivision(code="KE-04", name="Busia", type_="County"),
        KESubdivision(code="KE-05", name="Elgeyo/Marakwet", type_="County"),
        KESubdivision(code="KE-06", name="Embu", type_="County"),
        KESubdivision(code="KE-07", name="Garissa", type_="County"),
        KESubdivision(code="KE-08", name="Homa Bay", type_="County"),
        KESubdivision(code="KE-09", name="Isiolo", type_="County"),
        KESubdivision(code="KE-10", name="Kajiado", type_="County"),
        KESubdivision(code="KE-11", name="Kakamega", type_="County"),
        KESubdivision(code="KE-12", name="Kericho", type_="County"),
        KESubdivision(code="KE-13", name="Kiambu", type_="County"),
        KESubdivision(code="KE-14", name="Kilifi", type_="County"),
        KESubdivision(code="KE-15", name="Kirinyaga", type_="County"),
        KESubdivision(code="KE-16", name="Kisii", type_="County"),
        KESubdivision(code="KE-17", name="Kisumu", type_="County"),
        KESubdivision(code="KE-18", name="Kitui", type_="County"),
        KESubdivision(code="KE-19", name="Kwale", type_="County"),
        KESubdivision(code="KE-20", name="Laikipia", type_="County"),
        KESubdivision(code="KE-21", name="Lamu", type_="County"),
        KESubdivision(code="KE-22", name="Machakos", type_="County"),
        KESubdivision(code="KE-23", name="Makueni", type_="County"),
        KESubdivision(code="KE-24", name="Mandera", type_="County"),
        KESubdivision(code="KE-25", name="Marsabit", type_="County"),
        KESubdivision(code="KE-26", name="Meru", type_="County"),
        KESubdivision(code="KE-27", name="Migori", type_="County"),
        KESubdivision(code="KE-28", name="Mombasa", type_="County"),
        KESubdivision(code="KE-29", name="Murang'a", type_="County"),
        KESubdivision(code="KE-30", name="Nairobi City", type_="County"),
        KESubdivision(code="KE-31", name="Nakuru", type_="County"),
        KESubdivision(code="KE-32", name="Nandi", type_="County"),
        KESubdivision(code="KE-33", name="Narok", type_="County"),
        KESubdivision(code="KE-34", name="Nyamira", type_="County"),
        KESubdivision(code="KE-35", name="Nyandarua", type_="County"),
        KESubdivision(code="KE-36", name="Nyeri", type_="County"),
        KESubdivision(code="KE-37", name="Samburu", type_="County"),
        KESubdivision(code="KE-38", name="Siaya", type_="County"),
        KESubdivision(code="KE-39", name="Taita/Taveta", type_="County"),
        KESubdivision(code="KE-40", name="Tana River", type_="County"),
        KESubdivision(code="KE-41", name="Tharaka-Nithi", type_="County"),
        KESubdivision(code="KE-42", name="Trans Nzoia", type_="County"),
        KESubdivision(code="KE-43", name="Turkana", type_="County"),
        KESubdivision(code="KE-44", name="Uasin Gishu", type_="County"),
        KESubdivision(code="KE-45", name="Vihiga", type_="County"),
        KESubdivision(code="KE-46", name="Wajir", type_="County"),
        KESubdivision(code="KE-47", name="West Pokot", type_="County"),
    ],
)
