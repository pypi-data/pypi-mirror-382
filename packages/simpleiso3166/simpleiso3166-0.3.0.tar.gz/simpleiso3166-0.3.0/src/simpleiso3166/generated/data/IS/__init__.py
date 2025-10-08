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

ISSubdivisionCodeType = Literal[
    "IS-1",  # Höfuðborgarsvæði
    "IS-2",  # Suðurnes
    "IS-3",  # Vesturland
    "IS-4",  # Vestfirðir
    "IS-5",  # Norðurland vestra
    "IS-6",  # Norðurland eystra
    "IS-7",  # Austurland
    "IS-8",  # Suðurland
    "IS-AKN",  # Akraneskaupstaður
    "IS-AKU",  # Akureyrarbær
    "IS-ARN",  # Árneshreppur
    "IS-ASA",  # Ásahreppur
    "IS-BLA",  # Bláskógabyggð
    "IS-BOG",  # Borgarbyggð
    "IS-BOL",  # Bolungarvíkurkaupstaður
    "IS-DAB",  # Dalabyggð
    "IS-DAV",  # Dalvíkurbyggð
    "IS-EOM",  # Eyja- og Miklaholtshreppur
    "IS-EYF",  # Eyjafjarðarsveit
    "IS-FJD",  # Fjarðabyggð
    "IS-FJL",  # Fjallabyggð
    "IS-FLA",  # Flóahreppur
    "IS-FLR",  # Fljótsdalshreppur
    "IS-GAR",  # Garðabær
    "IS-GOG",  # Grímsnes- og Grafningshreppur
    "IS-GRN",  # Grindavíkurbær
    "IS-GRU",  # Grundarfjarðarbær
    "IS-GRY",  # Grýtubakkahreppur
    "IS-HAF",  # Hafnarfjarðarkaupstaður
    "IS-HRG",  # Hörgársveit
    "IS-HRU",  # Hrunamannahreppur
    "IS-HUG",  # Húnabyggð
    "IS-HUV",  # Húnaþing vestra
    "IS-HVA",  # Hvalfjarðarsveit
    "IS-HVE",  # Hveragerðisbær
    "IS-ISA",  # Ísafjarðarbær
    "IS-KAL",  # Kaldrananeshreppur
    "IS-KJO",  # Kjósarhreppur
    "IS-KOP",  # Kópavogsbær
    "IS-LAN",  # Langanesbyggð
    "IS-MOS",  # Mosfellsbær
    "IS-MUL",  # Múlaþing
    "IS-MYR",  # Mýrdalshreppur
    "IS-NOR",  # Norðurþing
    "IS-RGE",  # Rangárþing eystra
    "IS-RGY",  # Rangárþing ytra
    "IS-RHH",  # Reykhólahreppur
    "IS-RKN",  # Reykjanesbær
    "IS-RKV",  # Reykjavíkurborg
    "IS-SBT",  # Svalbarðsstrandarhreppur
    "IS-SDN",  # Suðurnesjabær
    "IS-SDV",  # Súðavíkurhreppur
    "IS-SEL",  # Seltjarnarnesbær
    "IS-SFA",  # Sveitarfélagið Árborg
    "IS-SHF",  # Sveitarfélagið Hornafjörður
    "IS-SKF",  # Skaftárhreppur
    "IS-SKG",  # Skagabyggð
    "IS-SKO",  # Skorradalshreppur
    "IS-SKR",  # Skagafjörður
    "IS-SNF",  # Snæfellsbær
    "IS-SOG",  # Skeiða- og Gnúpverjahreppur
    "IS-SOL",  # Sveitarfélagið Ölfus
    "IS-SSS",  # Sveitarfélagið Skagaströnd
    "IS-STR",  # Strandabyggð
    "IS-STY",  # Stykkishólmsbær
    "IS-SVG",  # Sveitarfélagið Vogar
    "IS-TAL",  # Tálknafjarðarhreppur
    "IS-THG",  # Þingeyjarsveit
    "IS-TJO",  # Tjörneshreppur
    "IS-VEM",  # Vestmannaeyjabær
    "IS-VER",  # Vesturbyggð
    "IS-VOP",  # Vopnafjarðarhreppur
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class ISSubdivision(Subdivision):
    code: ISSubdivisionCodeType


IS: Final[Country] = Country(
    alpha2="IS",
    alpha3="ISL",
    name="Iceland",
    common_name=None,
    official_name="Republic of Iceland",
    subdivisions=[
        ISSubdivision(code="IS-1", name="Höfuðborgarsvæði", type_="Region"),
        ISSubdivision(code="IS-2", name="Suðurnes", type_="Region"),
        ISSubdivision(code="IS-3", name="Vesturland", type_="Region"),
        ISSubdivision(code="IS-4", name="Vestfirðir", type_="Region"),
        ISSubdivision(code="IS-5", name="Norðurland vestra", type_="Region"),
        ISSubdivision(code="IS-6", name="Norðurland eystra", type_="Region"),
        ISSubdivision(code="IS-7", name="Austurland", type_="Region"),
        ISSubdivision(code="IS-8", name="Suðurland", type_="Region"),
        ISSubdivision(code="IS-AKN", name="Akraneskaupstaður", type_="Municipality"),
        ISSubdivision(code="IS-AKU", name="Akureyrarbær", type_="Municipality"),
        ISSubdivision(code="IS-ARN", name="Árneshreppur", type_="Municipality"),
        ISSubdivision(code="IS-ASA", name="Ásahreppur", type_="Municipality"),
        ISSubdivision(code="IS-BLA", name="Bláskógabyggð", type_="Municipality"),
        ISSubdivision(code="IS-BOG", name="Borgarbyggð", type_="Municipality"),
        ISSubdivision(code="IS-BOL", name="Bolungarvíkurkaupstaður", type_="Municipality"),
        ISSubdivision(code="IS-DAB", name="Dalabyggð", type_="Municipality"),
        ISSubdivision(code="IS-DAV", name="Dalvíkurbyggð", type_="Municipality"),
        ISSubdivision(code="IS-EOM", name="Eyja- og Miklaholtshreppur", type_="Municipality"),
        ISSubdivision(code="IS-EYF", name="Eyjafjarðarsveit", type_="Municipality"),
        ISSubdivision(code="IS-FJD", name="Fjarðabyggð", type_="Municipality"),
        ISSubdivision(code="IS-FJL", name="Fjallabyggð", type_="Municipality"),
        ISSubdivision(code="IS-FLA", name="Flóahreppur", type_="Municipality"),
        ISSubdivision(code="IS-FLR", name="Fljótsdalshreppur", type_="Municipality"),
        ISSubdivision(code="IS-GAR", name="Garðabær", type_="Municipality"),
        ISSubdivision(code="IS-GOG", name="Grímsnes- og Grafningshreppur", type_="Municipality"),
        ISSubdivision(code="IS-GRN", name="Grindavíkurbær", type_="Municipality"),
        ISSubdivision(code="IS-GRU", name="Grundarfjarðarbær", type_="Municipality"),
        ISSubdivision(code="IS-GRY", name="Grýtubakkahreppur", type_="Municipality"),
        ISSubdivision(code="IS-HAF", name="Hafnarfjarðarkaupstaður", type_="Municipality"),
        ISSubdivision(code="IS-HRG", name="Hörgársveit", type_="Municipality"),
        ISSubdivision(code="IS-HRU", name="Hrunamannahreppur", type_="Municipality"),
        ISSubdivision(code="IS-HUG", name="Húnabyggð", type_="Municipality"),
        ISSubdivision(code="IS-HUV", name="Húnaþing vestra", type_="Municipality"),
        ISSubdivision(code="IS-HVA", name="Hvalfjarðarsveit", type_="Municipality"),
        ISSubdivision(code="IS-HVE", name="Hveragerðisbær", type_="Municipality"),
        ISSubdivision(code="IS-ISA", name="Ísafjarðarbær", type_="Municipality"),
        ISSubdivision(code="IS-KAL", name="Kaldrananeshreppur", type_="Municipality"),
        ISSubdivision(code="IS-KJO", name="Kjósarhreppur", type_="Municipality"),
        ISSubdivision(code="IS-KOP", name="Kópavogsbær", type_="Municipality"),
        ISSubdivision(code="IS-LAN", name="Langanesbyggð", type_="Municipality"),
        ISSubdivision(code="IS-MOS", name="Mosfellsbær", type_="Municipality"),
        ISSubdivision(code="IS-MUL", name="Múlaþing", type_="Municipality"),
        ISSubdivision(code="IS-MYR", name="Mýrdalshreppur", type_="Municipality"),
        ISSubdivision(code="IS-NOR", name="Norðurþing", type_="Municipality"),
        ISSubdivision(code="IS-RGE", name="Rangárþing eystra", type_="Municipality"),
        ISSubdivision(code="IS-RGY", name="Rangárþing ytra", type_="Municipality"),
        ISSubdivision(code="IS-RHH", name="Reykhólahreppur", type_="Municipality"),
        ISSubdivision(code="IS-RKN", name="Reykjanesbær", type_="Municipality"),
        ISSubdivision(code="IS-RKV", name="Reykjavíkurborg", type_="Municipality"),
        ISSubdivision(code="IS-SBT", name="Svalbarðsstrandarhreppur", type_="Municipality"),
        ISSubdivision(code="IS-SDN", name="Suðurnesjabær", type_="Municipality"),
        ISSubdivision(code="IS-SDV", name="Súðavíkurhreppur", type_="Municipality"),
        ISSubdivision(code="IS-SEL", name="Seltjarnarnesbær", type_="Municipality"),
        ISSubdivision(code="IS-SFA", name="Sveitarfélagið Árborg", type_="Municipality"),
        ISSubdivision(code="IS-SHF", name="Sveitarfélagið Hornafjörður", type_="Municipality"),
        ISSubdivision(code="IS-SKF", name="Skaftárhreppur", type_="Municipality"),
        ISSubdivision(code="IS-SKG", name="Skagabyggð", type_="Municipality"),
        ISSubdivision(code="IS-SKO", name="Skorradalshreppur", type_="Municipality"),
        ISSubdivision(code="IS-SKR", name="Skagafjörður", type_="Municipality"),
        ISSubdivision(code="IS-SNF", name="Snæfellsbær", type_="Municipality"),
        ISSubdivision(code="IS-SOG", name="Skeiða- og Gnúpverjahreppur", type_="Municipality"),
        ISSubdivision(code="IS-SOL", name="Sveitarfélagið Ölfus", type_="Municipality"),
        ISSubdivision(code="IS-SSS", name="Sveitarfélagið Skagaströnd", type_="Municipality"),
        ISSubdivision(code="IS-STR", name="Strandabyggð", type_="Municipality"),
        ISSubdivision(code="IS-STY", name="Stykkishólmsbær", type_="Municipality"),
        ISSubdivision(code="IS-SVG", name="Sveitarfélagið Vogar", type_="Municipality"),
        ISSubdivision(code="IS-TAL", name="Tálknafjarðarhreppur", type_="Municipality"),
        ISSubdivision(code="IS-THG", name="Þingeyjarsveit", type_="Municipality"),
        ISSubdivision(code="IS-TJO", name="Tjörneshreppur", type_="Municipality"),
        ISSubdivision(code="IS-VEM", name="Vestmannaeyjabær", type_="Municipality"),
        ISSubdivision(code="IS-VER", name="Vesturbyggð", type_="Municipality"),
        ISSubdivision(code="IS-VOP", name="Vopnafjarðarhreppur", type_="Municipality"),
    ],
)
