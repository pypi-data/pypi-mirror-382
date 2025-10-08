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

BFSubdivisionCodeType = Literal[
    "BF-01",  # Boucle du Mouhoun
    "BF-02",  # Cascades
    "BF-03",  # Centre
    "BF-04",  # Centre-Est
    "BF-05",  # Centre-Nord
    "BF-06",  # Centre-Ouest
    "BF-07",  # Centre-Sud
    "BF-08",  # Est
    "BF-09",  # Hauts-Bassins
    "BF-10",  # Nord
    "BF-11",  # Plateau-Central
    "BF-12",  # Sahel
    "BF-13",  # Sud-Ouest
    "BF-BAL",  # Balé
    "BF-BAM",  # Bam
    "BF-BAN",  # Banwa
    "BF-BAZ",  # Bazèga
    "BF-BGR",  # Bougouriba
    "BF-BLG",  # Boulgou
    "BF-BLK",  # Boulkiemdé
    "BF-COM",  # Comoé
    "BF-GAN",  # Ganzourgou
    "BF-GNA",  # Gnagna
    "BF-GOU",  # Gourma
    "BF-HOU",  # Houet
    "BF-IOB",  # Ioba
    "BF-KAD",  # Kadiogo
    "BF-KEN",  # Kénédougou
    "BF-KMD",  # Komondjari
    "BF-KMP",  # Kompienga
    "BF-KOP",  # Koulpélogo
    "BF-KOS",  # Kossi
    "BF-KOT",  # Kouritenga
    "BF-KOW",  # Kourwéogo
    "BF-LER",  # Léraba
    "BF-LOR",  # Loroum
    "BF-MOU",  # Mouhoun
    "BF-NAM",  # Namentenga
    "BF-NAO",  # Nahouri
    "BF-NAY",  # Nayala
    "BF-NOU",  # Noumbiel
    "BF-OUB",  # Oubritenga
    "BF-OUD",  # Oudalan
    "BF-PAS",  # Passoré
    "BF-PON",  # Poni
    "BF-SEN",  # Séno
    "BF-SIS",  # Sissili
    "BF-SMT",  # Sanmatenga
    "BF-SNG",  # Sanguié
    "BF-SOM",  # Soum
    "BF-SOR",  # Sourou
    "BF-TAP",  # Tapoa
    "BF-TUI",  # Tuy
    "BF-YAG",  # Yagha
    "BF-YAT",  # Yatenga
    "BF-ZIR",  # Ziro
    "BF-ZON",  # Zondoma
    "BF-ZOU",  # Zoundwéogo
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BFSubdivision(Subdivision):
    code: BFSubdivisionCodeType


BF: Final[Country] = Country(
    alpha2="BF",
    alpha3="BFA",
    name="Burkina Faso",
    common_name=None,
    official_name=None,
    subdivisions=[
        BFSubdivision(code="BF-01", name="Boucle du Mouhoun", type_="Region"),
        BFSubdivision(code="BF-02", name="Cascades", type_="Region"),
        BFSubdivision(code="BF-03", name="Centre", type_="Region"),
        BFSubdivision(code="BF-04", name="Centre-Est", type_="Region"),
        BFSubdivision(code="BF-05", name="Centre-Nord", type_="Region"),
        BFSubdivision(code="BF-06", name="Centre-Ouest", type_="Region"),
        BFSubdivision(code="BF-07", name="Centre-Sud", type_="Region"),
        BFSubdivision(code="BF-08", name="Est", type_="Region"),
        BFSubdivision(code="BF-09", name="Hauts-Bassins", type_="Region"),
        BFSubdivision(code="BF-10", name="Nord", type_="Region"),
        BFSubdivision(code="BF-11", name="Plateau-Central", type_="Region"),
        BFSubdivision(code="BF-12", name="Sahel", type_="Region"),
        BFSubdivision(code="BF-13", name="Sud-Ouest", type_="Region"),
        BFSubdivision(code="BF-BAL", name="Balé", type_="Province"),
        BFSubdivision(code="BF-BAM", name="Bam", type_="Province"),
        BFSubdivision(code="BF-BAN", name="Banwa", type_="Province"),
        BFSubdivision(code="BF-BAZ", name="Bazèga", type_="Province"),
        BFSubdivision(code="BF-BGR", name="Bougouriba", type_="Province"),
        BFSubdivision(code="BF-BLG", name="Boulgou", type_="Province"),
        BFSubdivision(code="BF-BLK", name="Boulkiemdé", type_="Province"),
        BFSubdivision(code="BF-COM", name="Comoé", type_="Province"),
        BFSubdivision(code="BF-GAN", name="Ganzourgou", type_="Province"),
        BFSubdivision(code="BF-GNA", name="Gnagna", type_="Province"),
        BFSubdivision(code="BF-GOU", name="Gourma", type_="Province"),
        BFSubdivision(code="BF-HOU", name="Houet", type_="Province"),
        BFSubdivision(code="BF-IOB", name="Ioba", type_="Province"),
        BFSubdivision(code="BF-KAD", name="Kadiogo", type_="Province"),
        BFSubdivision(code="BF-KEN", name="Kénédougou", type_="Province"),
        BFSubdivision(code="BF-KMD", name="Komondjari", type_="Province"),
        BFSubdivision(code="BF-KMP", name="Kompienga", type_="Province"),
        BFSubdivision(code="BF-KOP", name="Koulpélogo", type_="Province"),
        BFSubdivision(code="BF-KOS", name="Kossi", type_="Province"),
        BFSubdivision(code="BF-KOT", name="Kouritenga", type_="Province"),
        BFSubdivision(code="BF-KOW", name="Kourwéogo", type_="Province"),
        BFSubdivision(code="BF-LER", name="Léraba", type_="Province"),
        BFSubdivision(code="BF-LOR", name="Loroum", type_="Province"),
        BFSubdivision(code="BF-MOU", name="Mouhoun", type_="Province"),
        BFSubdivision(code="BF-NAM", name="Namentenga", type_="Province"),
        BFSubdivision(code="BF-NAO", name="Nahouri", type_="Province"),
        BFSubdivision(code="BF-NAY", name="Nayala", type_="Province"),
        BFSubdivision(code="BF-NOU", name="Noumbiel", type_="Province"),
        BFSubdivision(code="BF-OUB", name="Oubritenga", type_="Province"),
        BFSubdivision(code="BF-OUD", name="Oudalan", type_="Province"),
        BFSubdivision(code="BF-PAS", name="Passoré", type_="Province"),
        BFSubdivision(code="BF-PON", name="Poni", type_="Province"),
        BFSubdivision(code="BF-SEN", name="Séno", type_="Province"),
        BFSubdivision(code="BF-SIS", name="Sissili", type_="Province"),
        BFSubdivision(code="BF-SMT", name="Sanmatenga", type_="Province"),
        BFSubdivision(code="BF-SNG", name="Sanguié", type_="Province"),
        BFSubdivision(code="BF-SOM", name="Soum", type_="Province"),
        BFSubdivision(code="BF-SOR", name="Sourou", type_="Province"),
        BFSubdivision(code="BF-TAP", name="Tapoa", type_="Province"),
        BFSubdivision(code="BF-TUI", name="Tuy", type_="Province"),
        BFSubdivision(code="BF-YAG", name="Yagha", type_="Province"),
        BFSubdivision(code="BF-YAT", name="Yatenga", type_="Province"),
        BFSubdivision(code="BF-ZIR", name="Ziro", type_="Province"),
        BFSubdivision(code="BF-ZON", name="Zondoma", type_="Province"),
        BFSubdivision(code="BF-ZOU", name="Zoundwéogo", type_="Province"),
    ],
)
