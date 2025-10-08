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

DZSubdivisionCodeType = Literal[
    "DZ-01",  # Adrar
    "DZ-02",  # Chlef
    "DZ-03",  # Laghouat
    "DZ-04",  # Oum el Bouaghi
    "DZ-05",  # Batna
    "DZ-06",  # Béjaïa
    "DZ-07",  # Biskra
    "DZ-08",  # Béchar
    "DZ-09",  # Blida
    "DZ-10",  # Bouira
    "DZ-11",  # Tamanrasset
    "DZ-12",  # Tébessa
    "DZ-13",  # Tlemcen
    "DZ-14",  # Tiaret
    "DZ-15",  # Tizi Ouzou
    "DZ-16",  # Alger
    "DZ-17",  # Djelfa
    "DZ-18",  # Jijel
    "DZ-19",  # Sétif
    "DZ-20",  # Saïda
    "DZ-21",  # Skikda
    "DZ-22",  # Sidi Bel Abbès
    "DZ-23",  # Annaba
    "DZ-24",  # Guelma
    "DZ-25",  # Constantine
    "DZ-26",  # Médéa
    "DZ-27",  # Mostaganem
    "DZ-28",  # M'sila
    "DZ-29",  # Mascara
    "DZ-30",  # Ouargla
    "DZ-31",  # Oran
    "DZ-32",  # El Bayadh
    "DZ-33",  # Illizi
    "DZ-34",  # Bordj Bou Arréridj
    "DZ-35",  # Boumerdès
    "DZ-36",  # El Tarf
    "DZ-37",  # Tindouf
    "DZ-38",  # Tissemsilt
    "DZ-39",  # El Oued
    "DZ-40",  # Khenchela
    "DZ-41",  # Souk Ahras
    "DZ-42",  # Tipaza
    "DZ-43",  # Mila
    "DZ-44",  # Aïn Defla
    "DZ-45",  # Naama
    "DZ-46",  # Aïn Témouchent
    "DZ-47",  # Ghardaïa
    "DZ-48",  # Relizane
    "DZ-49",  # Timimoun
    "DZ-50",  # Bordj Badji Mokhtar
    "DZ-51",  # Ouled Djellal
    "DZ-52",  # Béni Abbès
    "DZ-53",  # In Salah
    "DZ-54",  # In Guezzam
    "DZ-55",  # Touggourt
    "DZ-56",  # Djanet
    "DZ-57",  # El Meghaier
    "DZ-58",  # El Meniaa
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class DZSubdivision(Subdivision):
    code: DZSubdivisionCodeType


DZ: Final[Country] = Country(
    alpha2="DZ",
    alpha3="DZA",
    name="Algeria",
    common_name=None,
    official_name="People's Democratic Republic of Algeria",
    subdivisions=[
        DZSubdivision(code="DZ-01", name="Adrar", type_="Province"),
        DZSubdivision(code="DZ-02", name="Chlef", type_="Province"),
        DZSubdivision(code="DZ-03", name="Laghouat", type_="Province"),
        DZSubdivision(code="DZ-04", name="Oum el Bouaghi", type_="Province"),
        DZSubdivision(code="DZ-05", name="Batna", type_="Province"),
        DZSubdivision(code="DZ-06", name="Béjaïa", type_="Province"),
        DZSubdivision(code="DZ-07", name="Biskra", type_="Province"),
        DZSubdivision(code="DZ-08", name="Béchar", type_="Province"),
        DZSubdivision(code="DZ-09", name="Blida", type_="Province"),
        DZSubdivision(code="DZ-10", name="Bouira", type_="Province"),
        DZSubdivision(code="DZ-11", name="Tamanrasset", type_="Province"),
        DZSubdivision(code="DZ-12", name="Tébessa", type_="Province"),
        DZSubdivision(code="DZ-13", name="Tlemcen", type_="Province"),
        DZSubdivision(code="DZ-14", name="Tiaret", type_="Province"),
        DZSubdivision(code="DZ-15", name="Tizi Ouzou", type_="Province"),
        DZSubdivision(code="DZ-16", name="Alger", type_="Province"),
        DZSubdivision(code="DZ-17", name="Djelfa", type_="Province"),
        DZSubdivision(code="DZ-18", name="Jijel", type_="Province"),
        DZSubdivision(code="DZ-19", name="Sétif", type_="Province"),
        DZSubdivision(code="DZ-20", name="Saïda", type_="Province"),
        DZSubdivision(code="DZ-21", name="Skikda", type_="Province"),
        DZSubdivision(code="DZ-22", name="Sidi Bel Abbès", type_="Province"),
        DZSubdivision(code="DZ-23", name="Annaba", type_="Province"),
        DZSubdivision(code="DZ-24", name="Guelma", type_="Province"),
        DZSubdivision(code="DZ-25", name="Constantine", type_="Province"),
        DZSubdivision(code="DZ-26", name="Médéa", type_="Province"),
        DZSubdivision(code="DZ-27", name="Mostaganem", type_="Province"),
        DZSubdivision(code="DZ-28", name="M'sila", type_="Province"),
        DZSubdivision(code="DZ-29", name="Mascara", type_="Province"),
        DZSubdivision(code="DZ-30", name="Ouargla", type_="Province"),
        DZSubdivision(code="DZ-31", name="Oran", type_="Province"),
        DZSubdivision(code="DZ-32", name="El Bayadh", type_="Province"),
        DZSubdivision(code="DZ-33", name="Illizi", type_="Province"),
        DZSubdivision(code="DZ-34", name="Bordj Bou Arréridj", type_="Province"),
        DZSubdivision(code="DZ-35", name="Boumerdès", type_="Province"),
        DZSubdivision(code="DZ-36", name="El Tarf", type_="Province"),
        DZSubdivision(code="DZ-37", name="Tindouf", type_="Province"),
        DZSubdivision(code="DZ-38", name="Tissemsilt", type_="Province"),
        DZSubdivision(code="DZ-39", name="El Oued", type_="Province"),
        DZSubdivision(code="DZ-40", name="Khenchela", type_="Province"),
        DZSubdivision(code="DZ-41", name="Souk Ahras", type_="Province"),
        DZSubdivision(code="DZ-42", name="Tipaza", type_="Province"),
        DZSubdivision(code="DZ-43", name="Mila", type_="Province"),
        DZSubdivision(code="DZ-44", name="Aïn Defla", type_="Province"),
        DZSubdivision(code="DZ-45", name="Naama", type_="Province"),
        DZSubdivision(code="DZ-46", name="Aïn Témouchent", type_="Province"),
        DZSubdivision(code="DZ-47", name="Ghardaïa", type_="Province"),
        DZSubdivision(code="DZ-48", name="Relizane", type_="Province"),
        DZSubdivision(code="DZ-49", name="Timimoun", type_="Province"),
        DZSubdivision(code="DZ-50", name="Bordj Badji Mokhtar", type_="Province"),
        DZSubdivision(code="DZ-51", name="Ouled Djellal", type_="Province"),
        DZSubdivision(code="DZ-52", name="Béni Abbès", type_="Province"),
        DZSubdivision(code="DZ-53", name="In Salah", type_="Province"),
        DZSubdivision(code="DZ-54", name="In Guezzam", type_="Province"),
        DZSubdivision(code="DZ-55", name="Touggourt", type_="Province"),
        DZSubdivision(code="DZ-56", name="Djanet", type_="Province"),
        DZSubdivision(code="DZ-57", name="El Meghaier", type_="Province"),
        DZSubdivision(code="DZ-58", name="El Meniaa", type_="Province"),
    ],
)
