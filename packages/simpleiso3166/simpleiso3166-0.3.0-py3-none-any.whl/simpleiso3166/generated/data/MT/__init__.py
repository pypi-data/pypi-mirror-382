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

MTSubdivisionCodeType = Literal[
    "MT-01",  # Attard
    "MT-02",  # Balzan
    "MT-03",  # Birgu
    "MT-04",  # Birkirkara
    "MT-05",  # Birżebbuġa
    "MT-06",  # Bormla
    "MT-07",  # Dingli
    "MT-08",  # Fgura
    "MT-09",  # Floriana
    "MT-10",  # Fontana
    "MT-11",  # Gudja
    "MT-12",  # Gżira
    "MT-13",  # Għajnsielem
    "MT-14",  # Għarb
    "MT-15",  # Għargħur
    "MT-16",  # Għasri
    "MT-17",  # Għaxaq
    "MT-18",  # Ħamrun
    "MT-19",  # Iklin
    "MT-20",  # Isla
    "MT-21",  # Kalkara
    "MT-22",  # Kerċem
    "MT-23",  # Kirkop
    "MT-24",  # Lija
    "MT-25",  # Luqa
    "MT-26",  # Marsa
    "MT-27",  # Marsaskala
    "MT-28",  # Marsaxlokk
    "MT-29",  # Mdina
    "MT-30",  # Mellieħa
    "MT-31",  # Mġarr
    "MT-32",  # Mosta
    "MT-33",  # Mqabba
    "MT-34",  # Msida
    "MT-35",  # Mtarfa
    "MT-36",  # Munxar
    "MT-37",  # Nadur
    "MT-38",  # Naxxar
    "MT-39",  # Paola
    "MT-40",  # Pembroke
    "MT-41",  # Pietà
    "MT-42",  # Qala
    "MT-43",  # Qormi
    "MT-44",  # Qrendi
    "MT-45",  # Rabat Gozo
    "MT-46",  # Rabat Malta
    "MT-47",  # Safi
    "MT-48",  # Saint Julian's
    "MT-49",  # Saint John
    "MT-50",  # Saint Lawrence
    "MT-51",  # Saint Paul's Bay
    "MT-52",  # Sannat
    "MT-53",  # Saint Lucia's
    "MT-54",  # Santa Venera
    "MT-55",  # Siġġiewi
    "MT-56",  # Sliema
    "MT-57",  # Swieqi
    "MT-58",  # Ta' Xbiex
    "MT-59",  # Tarxien
    "MT-60",  # Valletta
    "MT-61",  # Xagħra
    "MT-62",  # Xewkija
    "MT-63",  # Xgħajra
    "MT-64",  # Żabbar
    "MT-65",  # Żebbuġ Gozo
    "MT-66",  # Żebbuġ Malta
    "MT-67",  # Żejtun
    "MT-68",  # Żurrieq
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MTSubdivision(Subdivision):
    code: MTSubdivisionCodeType


MT: Final[Country] = Country(
    alpha2="MT",
    alpha3="MLT",
    name="Malta",
    common_name=None,
    official_name="Republic of Malta",
    subdivisions=[
        MTSubdivision(code="MT-01", name="Attard", type_="Local council"),
        MTSubdivision(code="MT-02", name="Balzan", type_="Local council"),
        MTSubdivision(code="MT-03", name="Birgu", type_="Local council"),
        MTSubdivision(code="MT-04", name="Birkirkara", type_="Local council"),
        MTSubdivision(code="MT-05", name="Birżebbuġa", type_="Local council"),
        MTSubdivision(code="MT-06", name="Bormla", type_="Local council"),
        MTSubdivision(code="MT-07", name="Dingli", type_="Local council"),
        MTSubdivision(code="MT-08", name="Fgura", type_="Local council"),
        MTSubdivision(code="MT-09", name="Floriana", type_="Local council"),
        MTSubdivision(code="MT-10", name="Fontana", type_="Local council"),
        MTSubdivision(code="MT-11", name="Gudja", type_="Local council"),
        MTSubdivision(code="MT-12", name="Gżira", type_="Local council"),
        MTSubdivision(code="MT-13", name="Għajnsielem", type_="Local council"),
        MTSubdivision(code="MT-14", name="Għarb", type_="Local council"),
        MTSubdivision(code="MT-15", name="Għargħur", type_="Local council"),
        MTSubdivision(code="MT-16", name="Għasri", type_="Local council"),
        MTSubdivision(code="MT-17", name="Għaxaq", type_="Local council"),
        MTSubdivision(code="MT-18", name="Ħamrun", type_="Local council"),
        MTSubdivision(code="MT-19", name="Iklin", type_="Local council"),
        MTSubdivision(code="MT-20", name="Isla", type_="Local council"),
        MTSubdivision(code="MT-21", name="Kalkara", type_="Local council"),
        MTSubdivision(code="MT-22", name="Kerċem", type_="Local council"),
        MTSubdivision(code="MT-23", name="Kirkop", type_="Local council"),
        MTSubdivision(code="MT-24", name="Lija", type_="Local council"),
        MTSubdivision(code="MT-25", name="Luqa", type_="Local council"),
        MTSubdivision(code="MT-26", name="Marsa", type_="Local council"),
        MTSubdivision(code="MT-27", name="Marsaskala", type_="Local council"),
        MTSubdivision(code="MT-28", name="Marsaxlokk", type_="Local council"),
        MTSubdivision(code="MT-29", name="Mdina", type_="Local council"),
        MTSubdivision(code="MT-30", name="Mellieħa", type_="Local council"),
        MTSubdivision(code="MT-31", name="Mġarr", type_="Local council"),
        MTSubdivision(code="MT-32", name="Mosta", type_="Local council"),
        MTSubdivision(code="MT-33", name="Mqabba", type_="Local council"),
        MTSubdivision(code="MT-34", name="Msida", type_="Local council"),
        MTSubdivision(code="MT-35", name="Mtarfa", type_="Local council"),
        MTSubdivision(code="MT-36", name="Munxar", type_="Local council"),
        MTSubdivision(code="MT-37", name="Nadur", type_="Local council"),
        MTSubdivision(code="MT-38", name="Naxxar", type_="Local council"),
        MTSubdivision(code="MT-39", name="Paola", type_="Local council"),
        MTSubdivision(code="MT-40", name="Pembroke", type_="Local council"),
        MTSubdivision(code="MT-41", name="Pietà", type_="Local council"),
        MTSubdivision(code="MT-42", name="Qala", type_="Local council"),
        MTSubdivision(code="MT-43", name="Qormi", type_="Local council"),
        MTSubdivision(code="MT-44", name="Qrendi", type_="Local council"),
        MTSubdivision(code="MT-45", name="Rabat Gozo", type_="Local council"),
        MTSubdivision(code="MT-46", name="Rabat Malta", type_="Local council"),
        MTSubdivision(code="MT-47", name="Safi", type_="Local council"),
        MTSubdivision(code="MT-48", name="Saint Julian's", type_="Local council"),
        MTSubdivision(code="MT-49", name="Saint John", type_="Local council"),
        MTSubdivision(code="MT-50", name="Saint Lawrence", type_="Local council"),
        MTSubdivision(code="MT-51", name="Saint Paul's Bay", type_="Local council"),
        MTSubdivision(code="MT-52", name="Sannat", type_="Local council"),
        MTSubdivision(code="MT-53", name="Saint Lucia's", type_="Local council"),
        MTSubdivision(code="MT-54", name="Santa Venera", type_="Local council"),
        MTSubdivision(code="MT-55", name="Siġġiewi", type_="Local council"),
        MTSubdivision(code="MT-56", name="Sliema", type_="Local council"),
        MTSubdivision(code="MT-57", name="Swieqi", type_="Local council"),
        MTSubdivision(code="MT-58", name="Ta' Xbiex", type_="Local council"),
        MTSubdivision(code="MT-59", name="Tarxien", type_="Local council"),
        MTSubdivision(code="MT-60", name="Valletta", type_="Local council"),
        MTSubdivision(code="MT-61", name="Xagħra", type_="Local council"),
        MTSubdivision(code="MT-62", name="Xewkija", type_="Local council"),
        MTSubdivision(code="MT-63", name="Xgħajra", type_="Local council"),
        MTSubdivision(code="MT-64", name="Żabbar", type_="Local council"),
        MTSubdivision(code="MT-65", name="Żebbuġ Gozo", type_="Local council"),
        MTSubdivision(code="MT-66", name="Żebbuġ Malta", type_="Local council"),
        MTSubdivision(code="MT-67", name="Żejtun", type_="Local council"),
        MTSubdivision(code="MT-68", name="Żurrieq", type_="Local council"),
    ],
)
