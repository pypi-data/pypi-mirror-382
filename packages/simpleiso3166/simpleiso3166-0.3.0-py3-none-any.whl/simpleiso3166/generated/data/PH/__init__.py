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

PHSubdivisionCodeType = Literal[
    "PH-00",  # National Capital Region
    "PH-01",  # Ilocos (Region I)
    "PH-02",  # Cagayan Valley (Region II)
    "PH-03",  # Central Luzon (Region III)
    "PH-05",  # Bicol (Region V)
    "PH-06",  # Western Visayas (Region VI)
    "PH-07",  # Central Visayas (Region VII)
    "PH-08",  # Eastern Visayas (Region VIII)
    "PH-09",  # Zamboanga Peninsula (Region IX)
    "PH-10",  # Northern Mindanao (Region X)
    "PH-11",  # Davao (Region XI)
    "PH-12",  # Soccsksargen (Region XII)
    "PH-13",  # Caraga (Region XIII)
    "PH-14",  # Autonomous Region in Muslim Mindanao (ARMM)
    "PH-15",  # Cordillera Administrative Region (CAR)
    "PH-40",  # Calabarzon (Region IV-A)
    "PH-41",  # Mimaropa (Region IV-B)
    "PH-ABR",  # Abra
    "PH-AGN",  # Agusan del Norte
    "PH-AGS",  # Agusan del Sur
    "PH-AKL",  # Aklan
    "PH-ALB",  # Albay
    "PH-ANT",  # Antique
    "PH-APA",  # Apayao
    "PH-AUR",  # Aurora
    "PH-BAN",  # Bataan
    "PH-BAS",  # Basilan
    "PH-BEN",  # Benguet
    "PH-BIL",  # Biliran
    "PH-BOH",  # Bohol
    "PH-BTG",  # Batangas
    "PH-BTN",  # Batanes
    "PH-BUK",  # Bukidnon
    "PH-BUL",  # Bulacan
    "PH-CAG",  # Cagayan
    "PH-CAM",  # Camiguin
    "PH-CAN",  # Camarines Norte
    "PH-CAP",  # Capiz
    "PH-CAS",  # Camarines Sur
    "PH-CAT",  # Catanduanes
    "PH-CAV",  # Cavite
    "PH-CEB",  # Cebu
    "PH-COM",  # Davao de Oro
    "PH-DAO",  # Davao Oriental
    "PH-DAS",  # Davao del Sur
    "PH-DAV",  # Davao del Norte
    "PH-DIN",  # Dinagat Islands
    "PH-DVO",  # Davao Occidental
    "PH-EAS",  # Eastern Samar
    "PH-GUI",  # Guimaras
    "PH-IFU",  # Ifugao
    "PH-ILI",  # Iloilo
    "PH-ILN",  # Ilocos Norte
    "PH-ILS",  # Ilocos Sur
    "PH-ISA",  # Isabela
    "PH-KAL",  # Kalinga
    "PH-LAG",  # Laguna
    "PH-LAN",  # Lanao del Norte
    "PH-LAS",  # Lanao del Sur
    "PH-LEY",  # Leyte
    "PH-LUN",  # La Union
    "PH-MAD",  # Marinduque
    "PH-MAS",  # Masbate
    "PH-MDC",  # Mindoro Occidental
    "PH-MDR",  # Mindoro Oriental
    "PH-MGN",  # Maguindanao del Norte
    "PH-MGS",  # Maguindanao del Sur
    "PH-MOU",  # Mountain Province
    "PH-MSC",  # Misamis Occidental
    "PH-MSR",  # Misamis Oriental
    "PH-NCO",  # Cotabato
    "PH-NEC",  # Negros Occidental
    "PH-NER",  # Negros Oriental
    "PH-NSA",  # Northern Samar
    "PH-NUE",  # Nueva Ecija
    "PH-NUV",  # Nueva Vizcaya
    "PH-PAM",  # Pampanga
    "PH-PAN",  # Pangasinan
    "PH-PLW",  # Palawan
    "PH-QUE",  # Quezon
    "PH-QUI",  # Quirino
    "PH-RIZ",  # Rizal
    "PH-ROM",  # Romblon
    "PH-SAR",  # Sarangani
    "PH-SCO",  # South Cotabato
    "PH-SIG",  # Siquijor
    "PH-SLE",  # Southern Leyte
    "PH-SLU",  # Sulu
    "PH-SOR",  # Sorsogon
    "PH-SUK",  # Sultan Kudarat
    "PH-SUN",  # Surigao del Norte
    "PH-SUR",  # Surigao del Sur
    "PH-TAR",  # Tarlac
    "PH-TAW",  # Tawi-Tawi
    "PH-WSA",  # Samar
    "PH-ZAN",  # Zamboanga del Norte
    "PH-ZAS",  # Zamboanga del Sur
    "PH-ZMB",  # Zambales
    "PH-ZSI",  # Zamboanga Sibugay
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class PHSubdivision(Subdivision):
    code: PHSubdivisionCodeType


PH: Final[Country] = Country(
    alpha2="PH",
    alpha3="PHL",
    name="Philippines",
    common_name=None,
    official_name="Republic of the Philippines",
    subdivisions=[
        PHSubdivision(code="PH-00", name="National Capital Region", type_="Region"),
        PHSubdivision(code="PH-01", name="Ilocos (Region I)", type_="Region"),
        PHSubdivision(code="PH-02", name="Cagayan Valley (Region II)", type_="Region"),
        PHSubdivision(code="PH-03", name="Central Luzon (Region III)", type_="Region"),
        PHSubdivision(code="PH-05", name="Bicol (Region V)", type_="Region"),
        PHSubdivision(code="PH-06", name="Western Visayas (Region VI)", type_="Region"),
        PHSubdivision(code="PH-07", name="Central Visayas (Region VII)", type_="Region"),
        PHSubdivision(code="PH-08", name="Eastern Visayas (Region VIII)", type_="Region"),
        PHSubdivision(code="PH-09", name="Zamboanga Peninsula (Region IX)", type_="Region"),
        PHSubdivision(code="PH-10", name="Northern Mindanao (Region X)", type_="Region"),
        PHSubdivision(code="PH-11", name="Davao (Region XI)", type_="Region"),
        PHSubdivision(code="PH-12", name="Soccsksargen (Region XII)", type_="Region"),
        PHSubdivision(code="PH-13", name="Caraga (Region XIII)", type_="Region"),
        PHSubdivision(code="PH-14", name="Autonomous Region in Muslim Mindanao (ARMM)", type_="Region"),
        PHSubdivision(code="PH-15", name="Cordillera Administrative Region (CAR)", type_="Region"),
        PHSubdivision(code="PH-40", name="Calabarzon (Region IV-A)", type_="Region"),
        PHSubdivision(code="PH-41", name="Mimaropa (Region IV-B)", type_="Region"),
        PHSubdivision(code="PH-ABR", name="Abra", type_="Province"),
        PHSubdivision(code="PH-AGN", name="Agusan del Norte", type_="Province"),
        PHSubdivision(code="PH-AGS", name="Agusan del Sur", type_="Province"),
        PHSubdivision(code="PH-AKL", name="Aklan", type_="Province"),
        PHSubdivision(code="PH-ALB", name="Albay", type_="Province"),
        PHSubdivision(code="PH-ANT", name="Antique", type_="Province"),
        PHSubdivision(code="PH-APA", name="Apayao", type_="Province"),
        PHSubdivision(code="PH-AUR", name="Aurora", type_="Province"),
        PHSubdivision(code="PH-BAN", name="Bataan", type_="Province"),
        PHSubdivision(code="PH-BAS", name="Basilan", type_="Province"),
        PHSubdivision(code="PH-BEN", name="Benguet", type_="Province"),
        PHSubdivision(code="PH-BIL", name="Biliran", type_="Province"),
        PHSubdivision(code="PH-BOH", name="Bohol", type_="Province"),
        PHSubdivision(code="PH-BTG", name="Batangas", type_="Province"),
        PHSubdivision(code="PH-BTN", name="Batanes", type_="Province"),
        PHSubdivision(code="PH-BUK", name="Bukidnon", type_="Province"),
        PHSubdivision(code="PH-BUL", name="Bulacan", type_="Province"),
        PHSubdivision(code="PH-CAG", name="Cagayan", type_="Province"),
        PHSubdivision(code="PH-CAM", name="Camiguin", type_="Province"),
        PHSubdivision(code="PH-CAN", name="Camarines Norte", type_="Province"),
        PHSubdivision(code="PH-CAP", name="Capiz", type_="Province"),
        PHSubdivision(code="PH-CAS", name="Camarines Sur", type_="Province"),
        PHSubdivision(code="PH-CAT", name="Catanduanes", type_="Province"),
        PHSubdivision(code="PH-CAV", name="Cavite", type_="Province"),
        PHSubdivision(code="PH-CEB", name="Cebu", type_="Province"),
        PHSubdivision(code="PH-COM", name="Davao de Oro", type_="Province"),
        PHSubdivision(code="PH-DAO", name="Davao Oriental", type_="Province"),
        PHSubdivision(code="PH-DAS", name="Davao del Sur", type_="Province"),
        PHSubdivision(code="PH-DAV", name="Davao del Norte", type_="Province"),
        PHSubdivision(code="PH-DIN", name="Dinagat Islands", type_="Province"),
        PHSubdivision(code="PH-DVO", name="Davao Occidental", type_="Province"),
        PHSubdivision(code="PH-EAS", name="Eastern Samar", type_="Province"),
        PHSubdivision(code="PH-GUI", name="Guimaras", type_="Province"),
        PHSubdivision(code="PH-IFU", name="Ifugao", type_="Province"),
        PHSubdivision(code="PH-ILI", name="Iloilo", type_="Province"),
        PHSubdivision(code="PH-ILN", name="Ilocos Norte", type_="Province"),
        PHSubdivision(code="PH-ILS", name="Ilocos Sur", type_="Province"),
        PHSubdivision(code="PH-ISA", name="Isabela", type_="Province"),
        PHSubdivision(code="PH-KAL", name="Kalinga", type_="Province"),
        PHSubdivision(code="PH-LAG", name="Laguna", type_="Province"),
        PHSubdivision(code="PH-LAN", name="Lanao del Norte", type_="Province"),
        PHSubdivision(code="PH-LAS", name="Lanao del Sur", type_="Province"),
        PHSubdivision(code="PH-LEY", name="Leyte", type_="Province"),
        PHSubdivision(code="PH-LUN", name="La Union", type_="Province"),
        PHSubdivision(code="PH-MAD", name="Marinduque", type_="Province"),
        PHSubdivision(code="PH-MAS", name="Masbate", type_="Province"),
        PHSubdivision(code="PH-MDC", name="Mindoro Occidental", type_="Province"),
        PHSubdivision(code="PH-MDR", name="Mindoro Oriental", type_="Province"),
        PHSubdivision(code="PH-MGN", name="Maguindanao del Norte", type_="Province"),
        PHSubdivision(code="PH-MGS", name="Maguindanao del Sur", type_="Province"),
        PHSubdivision(code="PH-MOU", name="Mountain Province", type_="Province"),
        PHSubdivision(code="PH-MSC", name="Misamis Occidental", type_="Province"),
        PHSubdivision(code="PH-MSR", name="Misamis Oriental", type_="Province"),
        PHSubdivision(code="PH-NCO", name="Cotabato", type_="Province"),
        PHSubdivision(code="PH-NEC", name="Negros Occidental", type_="Province"),
        PHSubdivision(code="PH-NER", name="Negros Oriental", type_="Province"),
        PHSubdivision(code="PH-NSA", name="Northern Samar", type_="Province"),
        PHSubdivision(code="PH-NUE", name="Nueva Ecija", type_="Province"),
        PHSubdivision(code="PH-NUV", name="Nueva Vizcaya", type_="Province"),
        PHSubdivision(code="PH-PAM", name="Pampanga", type_="Province"),
        PHSubdivision(code="PH-PAN", name="Pangasinan", type_="Province"),
        PHSubdivision(code="PH-PLW", name="Palawan", type_="Province"),
        PHSubdivision(code="PH-QUE", name="Quezon", type_="Province"),
        PHSubdivision(code="PH-QUI", name="Quirino", type_="Province"),
        PHSubdivision(code="PH-RIZ", name="Rizal", type_="Province"),
        PHSubdivision(code="PH-ROM", name="Romblon", type_="Province"),
        PHSubdivision(code="PH-SAR", name="Sarangani", type_="Province"),
        PHSubdivision(code="PH-SCO", name="South Cotabato", type_="Province"),
        PHSubdivision(code="PH-SIG", name="Siquijor", type_="Province"),
        PHSubdivision(code="PH-SLE", name="Southern Leyte", type_="Province"),
        PHSubdivision(code="PH-SLU", name="Sulu", type_="Province"),
        PHSubdivision(code="PH-SOR", name="Sorsogon", type_="Province"),
        PHSubdivision(code="PH-SUK", name="Sultan Kudarat", type_="Province"),
        PHSubdivision(code="PH-SUN", name="Surigao del Norte", type_="Province"),
        PHSubdivision(code="PH-SUR", name="Surigao del Sur", type_="Province"),
        PHSubdivision(code="PH-TAR", name="Tarlac", type_="Province"),
        PHSubdivision(code="PH-TAW", name="Tawi-Tawi", type_="Province"),
        PHSubdivision(code="PH-WSA", name="Samar", type_="Province"),
        PHSubdivision(code="PH-ZAN", name="Zamboanga del Norte", type_="Province"),
        PHSubdivision(code="PH-ZAS", name="Zamboanga del Sur", type_="Province"),
        PHSubdivision(code="PH-ZMB", name="Zambales", type_="Province"),
        PHSubdivision(code="PH-ZSI", name="Zamboanga Sibugay", type_="Province"),
    ],
)
