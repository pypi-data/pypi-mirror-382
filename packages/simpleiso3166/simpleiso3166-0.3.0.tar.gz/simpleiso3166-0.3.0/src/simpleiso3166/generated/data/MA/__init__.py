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

MASubdivisionCodeType = Literal[
    "MA-01",  # Tanger-Tétouan-Al Hoceïma
    "MA-02",  # L'Oriental
    "MA-03",  # Fès-Meknès
    "MA-04",  # Rabat-Salé-Kénitra
    "MA-05",  # Béni Mellal-Khénifra
    "MA-06",  # Casablanca-Settat
    "MA-07",  # Marrakech-Safi
    "MA-08",  # Drâa-Tafilalet
    "MA-09",  # Souss-Massa
    "MA-10",  # Guelmim-Oued Noun (EH-partial)
    "MA-11",  # Laâyoune-Sakia El Hamra (EH-partial)
    "MA-12",  # Dakhla-Oued Ed-Dahab (EH)
    "MA-AGD",  # Agadir-Ida-Ou-Tanane
    "MA-AOU",  # Aousserd (EH)
    "MA-ASZ",  # Assa-Zag (EH-partial)
    "MA-AZI",  # Azilal
    "MA-BEM",  # Béni Mellal
    "MA-BER",  # Berkane
    "MA-BES",  # Benslimane
    "MA-BOD",  # Boujdour (EH)
    "MA-BOM",  # Boulemane
    "MA-BRR",  # Berrechid
    "MA-CAS",  # Casablanca
    "MA-CHE",  # Chefchaouen
    "MA-CHI",  # Chichaoua
    "MA-CHT",  # Chtouka-Ait Baha
    "MA-DRI",  # Driouch
    "MA-ERR",  # Errachidia
    "MA-ESI",  # Essaouira
    "MA-ESM",  # Es-Semara (EH-partial)
    "MA-FAH",  # Fahs-Anjra
    "MA-FES",  # Fès
    "MA-FIG",  # Figuig
    "MA-FQH",  # Fquih Ben Salah
    "MA-GUE",  # Guelmim
    "MA-GUF",  # Guercif
    "MA-HAJ",  # El Hajeb
    "MA-HAO",  # Al Haouz
    "MA-HOC",  # Al Hoceïma
    "MA-IFR",  # Ifrane
    "MA-INE",  # Inezgane-Ait Melloul
    "MA-JDI",  # El Jadida
    "MA-JRA",  # Jerada
    "MA-KEN",  # Kénitra
    "MA-KES",  # El Kelâa des Sraghna
    "MA-KHE",  # Khémisset
    "MA-KHN",  # Khénifra
    "MA-KHO",  # Khouribga
    "MA-LAA",  # Laâyoune (EH)
    "MA-LAR",  # Larache
    "MA-MAR",  # Marrakech
    "MA-MDF",  # M’diq-Fnideq
    "MA-MED",  # Médiouna
    "MA-MEK",  # Meknès
    "MA-MID",  # Midelt
    "MA-MOH",  # Mohammadia
    "MA-MOU",  # Moulay Yacoub
    "MA-NAD",  # Nador
    "MA-NOU",  # Nouaceur
    "MA-OUA",  # Ouarzazate
    "MA-OUD",  # Oued Ed-Dahab (EH)
    "MA-OUJ",  # Oujda-Angad
    "MA-OUZ",  # Ouezzane
    "MA-RAB",  # Rabat
    "MA-REH",  # Rehamna
    "MA-SAF",  # Safi
    "MA-SAL",  # Salé
    "MA-SEF",  # Sefrou
    "MA-SET",  # Settat
    "MA-SIB",  # Sidi Bennour
    "MA-SIF",  # Sidi Ifni
    "MA-SIK",  # Sidi Kacem
    "MA-SIL",  # Sidi Slimane
    "MA-SKH",  # Skhirate-Témara
    "MA-TAF",  # Tarfaya (EH-partial)
    "MA-TAI",  # Taourirt
    "MA-TAO",  # Taounate
    "MA-TAR",  # Taroudannt
    "MA-TAT",  # Tata
    "MA-TAZ",  # Taza
    "MA-TET",  # Tétouan
    "MA-TIN",  # Tinghir
    "MA-TIZ",  # Tiznit
    "MA-TNG",  # Tanger-Assilah
    "MA-TNT",  # Tan-Tan (EH-partial)
    "MA-YUS",  # Youssoufia
    "MA-ZAG",  # Zagora
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MASubdivision(Subdivision):
    code: MASubdivisionCodeType


MA: Final[Country] = Country(
    alpha2="MA",
    alpha3="MAR",
    name="Morocco",
    common_name=None,
    official_name="Kingdom of Morocco",
    subdivisions=[
        MASubdivision(code="MA-01", name="Tanger-Tétouan-Al Hoceïma", type_="Region"),
        MASubdivision(code="MA-02", name="L'Oriental", type_="Region"),
        MASubdivision(code="MA-03", name="Fès-Meknès", type_="Region"),
        MASubdivision(code="MA-04", name="Rabat-Salé-Kénitra", type_="Region"),
        MASubdivision(code="MA-05", name="Béni Mellal-Khénifra", type_="Region"),
        MASubdivision(code="MA-06", name="Casablanca-Settat", type_="Region"),
        MASubdivision(code="MA-07", name="Marrakech-Safi", type_="Region"),
        MASubdivision(code="MA-08", name="Drâa-Tafilalet", type_="Region"),
        MASubdivision(code="MA-09", name="Souss-Massa", type_="Region"),
        MASubdivision(code="MA-10", name="Guelmim-Oued Noun (EH-partial)", type_="Region"),
        MASubdivision(code="MA-11", name="Laâyoune-Sakia El Hamra (EH-partial)", type_="Region"),
        MASubdivision(code="MA-12", name="Dakhla-Oued Ed-Dahab (EH)", type_="Region"),
        MASubdivision(code="MA-AGD", name="Agadir-Ida-Ou-Tanane", type_="Prefecture"),
        MASubdivision(code="MA-AOU", name="Aousserd (EH)", type_="Province"),
        MASubdivision(code="MA-ASZ", name="Assa-Zag (EH-partial)", type_="Province"),
        MASubdivision(code="MA-AZI", name="Azilal", type_="Province"),
        MASubdivision(code="MA-BEM", name="Béni Mellal", type_="Province"),
        MASubdivision(code="MA-BER", name="Berkane", type_="Province"),
        MASubdivision(code="MA-BES", name="Benslimane", type_="Province"),
        MASubdivision(code="MA-BOD", name="Boujdour (EH)", type_="Province"),
        MASubdivision(code="MA-BOM", name="Boulemane", type_="Province"),
        MASubdivision(code="MA-BRR", name="Berrechid", type_="Province"),
        MASubdivision(code="MA-CAS", name="Casablanca", type_="Prefecture"),
        MASubdivision(code="MA-CHE", name="Chefchaouen", type_="Province"),
        MASubdivision(code="MA-CHI", name="Chichaoua", type_="Province"),
        MASubdivision(code="MA-CHT", name="Chtouka-Ait Baha", type_="Province"),
        MASubdivision(code="MA-DRI", name="Driouch", type_="Province"),
        MASubdivision(code="MA-ERR", name="Errachidia", type_="Province"),
        MASubdivision(code="MA-ESI", name="Essaouira", type_="Province"),
        MASubdivision(code="MA-ESM", name="Es-Semara (EH-partial)", type_="Province"),
        MASubdivision(code="MA-FAH", name="Fahs-Anjra", type_="Province"),
        MASubdivision(code="MA-FES", name="Fès", type_="Prefecture"),
        MASubdivision(code="MA-FIG", name="Figuig", type_="Province"),
        MASubdivision(code="MA-FQH", name="Fquih Ben Salah", type_="Province"),
        MASubdivision(code="MA-GUE", name="Guelmim", type_="Province"),
        MASubdivision(code="MA-GUF", name="Guercif", type_="Province"),
        MASubdivision(code="MA-HAJ", name="El Hajeb", type_="Province"),
        MASubdivision(code="MA-HAO", name="Al Haouz", type_="Province"),
        MASubdivision(code="MA-HOC", name="Al Hoceïma", type_="Province"),
        MASubdivision(code="MA-IFR", name="Ifrane", type_="Province"),
        MASubdivision(code="MA-INE", name="Inezgane-Ait Melloul", type_="Prefecture"),
        MASubdivision(code="MA-JDI", name="El Jadida", type_="Province"),
        MASubdivision(code="MA-JRA", name="Jerada", type_="Province"),
        MASubdivision(code="MA-KEN", name="Kénitra", type_="Province"),
        MASubdivision(code="MA-KES", name="El Kelâa des Sraghna", type_="Province"),
        MASubdivision(code="MA-KHE", name="Khémisset", type_="Province"),
        MASubdivision(code="MA-KHN", name="Khénifra", type_="Province"),
        MASubdivision(code="MA-KHO", name="Khouribga", type_="Province"),
        MASubdivision(code="MA-LAA", name="Laâyoune (EH)", type_="Province"),
        MASubdivision(code="MA-LAR", name="Larache", type_="Province"),
        MASubdivision(code="MA-MAR", name="Marrakech", type_="Prefecture"),
        MASubdivision(code="MA-MDF", name="M’diq-Fnideq", type_="Prefecture"),
        MASubdivision(code="MA-MED", name="Médiouna", type_="Province"),
        MASubdivision(code="MA-MEK", name="Meknès", type_="Prefecture"),
        MASubdivision(code="MA-MID", name="Midelt", type_="Province"),
        MASubdivision(code="MA-MOH", name="Mohammadia", type_="Prefecture"),
        MASubdivision(code="MA-MOU", name="Moulay Yacoub", type_="Province"),
        MASubdivision(code="MA-NAD", name="Nador", type_="Province"),
        MASubdivision(code="MA-NOU", name="Nouaceur", type_="Province"),
        MASubdivision(code="MA-OUA", name="Ouarzazate", type_="Province"),
        MASubdivision(code="MA-OUD", name="Oued Ed-Dahab (EH)", type_="Province"),
        MASubdivision(code="MA-OUJ", name="Oujda-Angad", type_="Prefecture"),
        MASubdivision(code="MA-OUZ", name="Ouezzane", type_="Province"),
        MASubdivision(code="MA-RAB", name="Rabat", type_="Prefecture"),
        MASubdivision(code="MA-REH", name="Rehamna", type_="Province"),
        MASubdivision(code="MA-SAF", name="Safi", type_="Province"),
        MASubdivision(code="MA-SAL", name="Salé", type_="Prefecture"),
        MASubdivision(code="MA-SEF", name="Sefrou", type_="Province"),
        MASubdivision(code="MA-SET", name="Settat", type_="Province"),
        MASubdivision(code="MA-SIB", name="Sidi Bennour", type_="Province"),
        MASubdivision(code="MA-SIF", name="Sidi Ifni", type_="Province"),
        MASubdivision(code="MA-SIK", name="Sidi Kacem", type_="Province"),
        MASubdivision(code="MA-SIL", name="Sidi Slimane", type_="Province"),
        MASubdivision(code="MA-SKH", name="Skhirate-Témara", type_="Prefecture"),
        MASubdivision(code="MA-TAF", name="Tarfaya (EH-partial)", type_="Province"),
        MASubdivision(code="MA-TAI", name="Taourirt", type_="Province"),
        MASubdivision(code="MA-TAO", name="Taounate", type_="Province"),
        MASubdivision(code="MA-TAR", name="Taroudannt", type_="Province"),
        MASubdivision(code="MA-TAT", name="Tata", type_="Province"),
        MASubdivision(code="MA-TAZ", name="Taza", type_="Province"),
        MASubdivision(code="MA-TET", name="Tétouan", type_="Province"),
        MASubdivision(code="MA-TIN", name="Tinghir", type_="Province"),
        MASubdivision(code="MA-TIZ", name="Tiznit", type_="Province"),
        MASubdivision(code="MA-TNG", name="Tanger-Assilah", type_="Prefecture"),
        MASubdivision(code="MA-TNT", name="Tan-Tan (EH-partial)", type_="Province"),
        MASubdivision(code="MA-YUS", name="Youssoufia", type_="Province"),
        MASubdivision(code="MA-ZAG", name="Zagora", type_="Province"),
    ],
)
