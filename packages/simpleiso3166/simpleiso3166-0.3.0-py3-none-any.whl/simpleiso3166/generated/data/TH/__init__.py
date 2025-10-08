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

THSubdivisionCodeType = Literal[
    "TH-10",  # Krung Thep Maha Nakhon
    "TH-11",  # Samut Prakan
    "TH-12",  # Nonthaburi
    "TH-13",  # Pathum Thani
    "TH-14",  # Phra Nakhon Si Ayutthaya
    "TH-15",  # Ang Thong
    "TH-16",  # Lop Buri
    "TH-17",  # Sing Buri
    "TH-18",  # Chai Nat
    "TH-19",  # Saraburi
    "TH-20",  # Chon Buri
    "TH-21",  # Rayong
    "TH-22",  # Chanthaburi
    "TH-23",  # Trat
    "TH-24",  # Chachoengsao
    "TH-25",  # Prachin Buri
    "TH-26",  # Nakhon Nayok
    "TH-27",  # Sa Kaeo
    "TH-30",  # Nakhon Ratchasima
    "TH-31",  # Buri Ram
    "TH-32",  # Surin
    "TH-33",  # Si Sa Ket
    "TH-34",  # Ubon Ratchathani
    "TH-35",  # Yasothon
    "TH-36",  # Chaiyaphum
    "TH-37",  # Amnat Charoen
    "TH-38",  # Bueng Kan
    "TH-39",  # Nong Bua Lam Phu
    "TH-40",  # Khon Kaen
    "TH-41",  # Udon Thani
    "TH-42",  # Loei
    "TH-43",  # Nong Khai
    "TH-44",  # Maha Sarakham
    "TH-45",  # Roi Et
    "TH-46",  # Kalasin
    "TH-47",  # Sakon Nakhon
    "TH-48",  # Nakhon Phanom
    "TH-49",  # Mukdahan
    "TH-50",  # Chiang Mai
    "TH-51",  # Lamphun
    "TH-52",  # Lampang
    "TH-53",  # Uttaradit
    "TH-54",  # Phrae
    "TH-55",  # Nan
    "TH-56",  # Phayao
    "TH-57",  # Chiang Rai
    "TH-58",  # Mae Hong Son
    "TH-60",  # Nakhon Sawan
    "TH-61",  # Uthai Thani
    "TH-62",  # Kamphaeng Phet
    "TH-63",  # Tak
    "TH-64",  # Sukhothai
    "TH-65",  # Phitsanulok
    "TH-66",  # Phichit
    "TH-67",  # Phetchabun
    "TH-70",  # Ratchaburi
    "TH-71",  # Kanchanaburi
    "TH-72",  # Suphan Buri
    "TH-73",  # Nakhon Pathom
    "TH-74",  # Samut Sakhon
    "TH-75",  # Samut Songkhram
    "TH-76",  # Phetchaburi
    "TH-77",  # Prachuap Khiri Khan
    "TH-80",  # Nakhon Si Thammarat
    "TH-81",  # Krabi
    "TH-82",  # Phangnga
    "TH-83",  # Phuket
    "TH-84",  # Surat Thani
    "TH-85",  # Ranong
    "TH-86",  # Chumphon
    "TH-90",  # Songkhla
    "TH-91",  # Satun
    "TH-92",  # Trang
    "TH-93",  # Phatthalung
    "TH-94",  # Pattani
    "TH-95",  # Yala
    "TH-96",  # Narathiwat
    "TH-S",  # Phatthaya
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class THSubdivision(Subdivision):
    code: THSubdivisionCodeType


TH: Final[Country] = Country(
    alpha2="TH",
    alpha3="THA",
    name="Thailand",
    common_name=None,
    official_name="Kingdom of Thailand",
    subdivisions=[
        THSubdivision(code="TH-10", name="Krung Thep Maha Nakhon", type_="Metropolitan administration"),
        THSubdivision(code="TH-11", name="Samut Prakan", type_="Province"),
        THSubdivision(code="TH-12", name="Nonthaburi", type_="Province"),
        THSubdivision(code="TH-13", name="Pathum Thani", type_="Province"),
        THSubdivision(code="TH-14", name="Phra Nakhon Si Ayutthaya", type_="Province"),
        THSubdivision(code="TH-15", name="Ang Thong", type_="Province"),
        THSubdivision(code="TH-16", name="Lop Buri", type_="Province"),
        THSubdivision(code="TH-17", name="Sing Buri", type_="Province"),
        THSubdivision(code="TH-18", name="Chai Nat", type_="Province"),
        THSubdivision(code="TH-19", name="Saraburi", type_="Province"),
        THSubdivision(code="TH-20", name="Chon Buri", type_="Province"),
        THSubdivision(code="TH-21", name="Rayong", type_="Province"),
        THSubdivision(code="TH-22", name="Chanthaburi", type_="Province"),
        THSubdivision(code="TH-23", name="Trat", type_="Province"),
        THSubdivision(code="TH-24", name="Chachoengsao", type_="Province"),
        THSubdivision(code="TH-25", name="Prachin Buri", type_="Province"),
        THSubdivision(code="TH-26", name="Nakhon Nayok", type_="Province"),
        THSubdivision(code="TH-27", name="Sa Kaeo", type_="Province"),
        THSubdivision(code="TH-30", name="Nakhon Ratchasima", type_="Province"),
        THSubdivision(code="TH-31", name="Buri Ram", type_="Province"),
        THSubdivision(code="TH-32", name="Surin", type_="Province"),
        THSubdivision(code="TH-33", name="Si Sa Ket", type_="Province"),
        THSubdivision(code="TH-34", name="Ubon Ratchathani", type_="Province"),
        THSubdivision(code="TH-35", name="Yasothon", type_="Province"),
        THSubdivision(code="TH-36", name="Chaiyaphum", type_="Province"),
        THSubdivision(code="TH-37", name="Amnat Charoen", type_="Province"),
        THSubdivision(code="TH-38", name="Bueng Kan", type_="Province"),
        THSubdivision(code="TH-39", name="Nong Bua Lam Phu", type_="Province"),
        THSubdivision(code="TH-40", name="Khon Kaen", type_="Province"),
        THSubdivision(code="TH-41", name="Udon Thani", type_="Province"),
        THSubdivision(code="TH-42", name="Loei", type_="Province"),
        THSubdivision(code="TH-43", name="Nong Khai", type_="Province"),
        THSubdivision(code="TH-44", name="Maha Sarakham", type_="Province"),
        THSubdivision(code="TH-45", name="Roi Et", type_="Province"),
        THSubdivision(code="TH-46", name="Kalasin", type_="Province"),
        THSubdivision(code="TH-47", name="Sakon Nakhon", type_="Province"),
        THSubdivision(code="TH-48", name="Nakhon Phanom", type_="Province"),
        THSubdivision(code="TH-49", name="Mukdahan", type_="Province"),
        THSubdivision(code="TH-50", name="Chiang Mai", type_="Province"),
        THSubdivision(code="TH-51", name="Lamphun", type_="Province"),
        THSubdivision(code="TH-52", name="Lampang", type_="Province"),
        THSubdivision(code="TH-53", name="Uttaradit", type_="Province"),
        THSubdivision(code="TH-54", name="Phrae", type_="Province"),
        THSubdivision(code="TH-55", name="Nan", type_="Province"),
        THSubdivision(code="TH-56", name="Phayao", type_="Province"),
        THSubdivision(code="TH-57", name="Chiang Rai", type_="Province"),
        THSubdivision(code="TH-58", name="Mae Hong Son", type_="Province"),
        THSubdivision(code="TH-60", name="Nakhon Sawan", type_="Province"),
        THSubdivision(code="TH-61", name="Uthai Thani", type_="Province"),
        THSubdivision(code="TH-62", name="Kamphaeng Phet", type_="Province"),
        THSubdivision(code="TH-63", name="Tak", type_="Province"),
        THSubdivision(code="TH-64", name="Sukhothai", type_="Province"),
        THSubdivision(code="TH-65", name="Phitsanulok", type_="Province"),
        THSubdivision(code="TH-66", name="Phichit", type_="Province"),
        THSubdivision(code="TH-67", name="Phetchabun", type_="Province"),
        THSubdivision(code="TH-70", name="Ratchaburi", type_="Province"),
        THSubdivision(code="TH-71", name="Kanchanaburi", type_="Province"),
        THSubdivision(code="TH-72", name="Suphan Buri", type_="Province"),
        THSubdivision(code="TH-73", name="Nakhon Pathom", type_="Province"),
        THSubdivision(code="TH-74", name="Samut Sakhon", type_="Province"),
        THSubdivision(code="TH-75", name="Samut Songkhram", type_="Province"),
        THSubdivision(code="TH-76", name="Phetchaburi", type_="Province"),
        THSubdivision(code="TH-77", name="Prachuap Khiri Khan", type_="Province"),
        THSubdivision(code="TH-80", name="Nakhon Si Thammarat", type_="Province"),
        THSubdivision(code="TH-81", name="Krabi", type_="Province"),
        THSubdivision(code="TH-82", name="Phangnga", type_="Province"),
        THSubdivision(code="TH-83", name="Phuket", type_="Province"),
        THSubdivision(code="TH-84", name="Surat Thani", type_="Province"),
        THSubdivision(code="TH-85", name="Ranong", type_="Province"),
        THSubdivision(code="TH-86", name="Chumphon", type_="Province"),
        THSubdivision(code="TH-90", name="Songkhla", type_="Province"),
        THSubdivision(code="TH-91", name="Satun", type_="Province"),
        THSubdivision(code="TH-92", name="Trang", type_="Province"),
        THSubdivision(code="TH-93", name="Phatthalung", type_="Province"),
        THSubdivision(code="TH-94", name="Pattani", type_="Province"),
        THSubdivision(code="TH-95", name="Yala", type_="Province"),
        THSubdivision(code="TH-96", name="Narathiwat", type_="Province"),
        THSubdivision(code="TH-S", name="Phatthaya", type_="Special administrative city"),
    ],
)
