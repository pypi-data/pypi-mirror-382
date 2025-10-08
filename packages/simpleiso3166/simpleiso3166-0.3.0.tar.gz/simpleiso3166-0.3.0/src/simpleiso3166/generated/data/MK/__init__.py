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

MKSubdivisionCodeType = Literal[
    "MK-101",  # Veles
    "MK-102",  # Gradsko
    "MK-103",  # Demir Kapija
    "MK-104",  # Kavadarci
    "MK-105",  # Lozovo
    "MK-106",  # Negotino
    "MK-107",  # Rosoman
    "MK-108",  # Sveti Nikole
    "MK-109",  # Čaška
    "MK-201",  # Berovo
    "MK-202",  # Vinica
    "MK-203",  # Delčevo
    "MK-204",  # Zrnovci
    "MK-205",  # Karbinci
    "MK-206",  # Kočani
    "MK-207",  # Makedonska Kamenica
    "MK-208",  # Pehčevo
    "MK-209",  # Probištip
    "MK-210",  # Češinovo-Obleševo
    "MK-211",  # Štip
    "MK-301",  # Vevčani
    "MK-303",  # Debar
    "MK-304",  # Debrca
    "MK-307",  # Kičevo
    "MK-308",  # Makedonski Brod
    "MK-310",  # Ohrid
    "MK-311",  # Plasnica
    "MK-312",  # Struga
    "MK-313",  # Centar Župa
    "MK-401",  # Bogdanci
    "MK-402",  # Bosilovo
    "MK-403",  # Valandovo
    "MK-404",  # Vasilevo
    "MK-405",  # Gevgelija
    "MK-406",  # Dojran
    "MK-407",  # Konče
    "MK-408",  # Novo Selo
    "MK-409",  # Radoviš
    "MK-410",  # Strumica
    "MK-501",  # Bitola
    "MK-502",  # Demir Hisar
    "MK-503",  # Dolneni
    "MK-504",  # Krivogaštani
    "MK-505",  # Kruševo
    "MK-506",  # Mogila
    "MK-507",  # Novaci
    "MK-508",  # Prilep
    "MK-509",  # Resen
    "MK-601",  # Bogovinje
    "MK-602",  # Brvenica
    "MK-603",  # Vrapčište
    "MK-604",  # Gostivar
    "MK-605",  # Želino
    "MK-606",  # Jegunovce
    "MK-607",  # Mavrovo i Rostuše
    "MK-608",  # Tearce
    "MK-609",  # Tetovo
    "MK-701",  # Kratovo
    "MK-702",  # Kriva Palanka
    "MK-703",  # Kumanovo
    "MK-704",  # Lipkovo
    "MK-705",  # Rankovce
    "MK-706",  # Staro Nagoričane
    "MK-801",  # Aerodrom †
    "MK-802",  # Aračinovo
    "MK-803",  # Butel †
    "MK-804",  # Gazi Baba †
    "MK-805",  # Gjorče Petrov †
    "MK-806",  # Zelenikovo
    "MK-807",  # Ilinden
    "MK-808",  # Karpoš †
    "MK-809",  # Kisela Voda †
    "MK-810",  # Petrovec
    "MK-811",  # Saraj †
    "MK-812",  # Sopište
    "MK-813",  # Studeničani
    "MK-814",  # Centar †
    "MK-815",  # Čair †
    "MK-816",  # Čučer-Sandevo
    "MK-817",  # Šuto Orizari †
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MKSubdivision(Subdivision):
    code: MKSubdivisionCodeType


MK: Final[Country] = Country(
    alpha2="MK",
    alpha3="MKD",
    name="North Macedonia",
    common_name=None,
    official_name="Republic of North Macedonia",
    subdivisions=[
        MKSubdivision(code="MK-101", name="Veles", type_="Municipality"),
        MKSubdivision(code="MK-102", name="Gradsko", type_="Municipality"),
        MKSubdivision(code="MK-103", name="Demir Kapija", type_="Municipality"),
        MKSubdivision(code="MK-104", name="Kavadarci", type_="Municipality"),
        MKSubdivision(code="MK-105", name="Lozovo", type_="Municipality"),
        MKSubdivision(code="MK-106", name="Negotino", type_="Municipality"),
        MKSubdivision(code="MK-107", name="Rosoman", type_="Municipality"),
        MKSubdivision(code="MK-108", name="Sveti Nikole", type_="Municipality"),
        MKSubdivision(code="MK-109", name="Čaška", type_="Municipality"),
        MKSubdivision(code="MK-201", name="Berovo", type_="Municipality"),
        MKSubdivision(code="MK-202", name="Vinica", type_="Municipality"),
        MKSubdivision(code="MK-203", name="Delčevo", type_="Municipality"),
        MKSubdivision(code="MK-204", name="Zrnovci", type_="Municipality"),
        MKSubdivision(code="MK-205", name="Karbinci", type_="Municipality"),
        MKSubdivision(code="MK-206", name="Kočani", type_="Municipality"),
        MKSubdivision(code="MK-207", name="Makedonska Kamenica", type_="Municipality"),
        MKSubdivision(code="MK-208", name="Pehčevo", type_="Municipality"),
        MKSubdivision(code="MK-209", name="Probištip", type_="Municipality"),
        MKSubdivision(code="MK-210", name="Češinovo-Obleševo", type_="Municipality"),
        MKSubdivision(code="MK-211", name="Štip", type_="Municipality"),
        MKSubdivision(code="MK-301", name="Vevčani", type_="Municipality"),
        MKSubdivision(code="MK-303", name="Debar", type_="Municipality"),
        MKSubdivision(code="MK-304", name="Debrca", type_="Municipality"),
        MKSubdivision(code="MK-307", name="Kičevo", type_="Municipality"),
        MKSubdivision(code="MK-308", name="Makedonski Brod", type_="Municipality"),
        MKSubdivision(code="MK-310", name="Ohrid", type_="Municipality"),
        MKSubdivision(code="MK-311", name="Plasnica", type_="Municipality"),
        MKSubdivision(code="MK-312", name="Struga", type_="Municipality"),
        MKSubdivision(code="MK-313", name="Centar Župa", type_="Municipality"),
        MKSubdivision(code="MK-401", name="Bogdanci", type_="Municipality"),
        MKSubdivision(code="MK-402", name="Bosilovo", type_="Municipality"),
        MKSubdivision(code="MK-403", name="Valandovo", type_="Municipality"),
        MKSubdivision(code="MK-404", name="Vasilevo", type_="Municipality"),
        MKSubdivision(code="MK-405", name="Gevgelija", type_="Municipality"),
        MKSubdivision(code="MK-406", name="Dojran", type_="Municipality"),
        MKSubdivision(code="MK-407", name="Konče", type_="Municipality"),
        MKSubdivision(code="MK-408", name="Novo Selo", type_="Municipality"),
        MKSubdivision(code="MK-409", name="Radoviš", type_="Municipality"),
        MKSubdivision(code="MK-410", name="Strumica", type_="Municipality"),
        MKSubdivision(code="MK-501", name="Bitola", type_="Municipality"),
        MKSubdivision(code="MK-502", name="Demir Hisar", type_="Municipality"),
        MKSubdivision(code="MK-503", name="Dolneni", type_="Municipality"),
        MKSubdivision(code="MK-504", name="Krivogaštani", type_="Municipality"),
        MKSubdivision(code="MK-505", name="Kruševo", type_="Municipality"),
        MKSubdivision(code="MK-506", name="Mogila", type_="Municipality"),
        MKSubdivision(code="MK-507", name="Novaci", type_="Municipality"),
        MKSubdivision(code="MK-508", name="Prilep", type_="Municipality"),
        MKSubdivision(code="MK-509", name="Resen", type_="Municipality"),
        MKSubdivision(code="MK-601", name="Bogovinje", type_="Municipality"),
        MKSubdivision(code="MK-602", name="Brvenica", type_="Municipality"),
        MKSubdivision(code="MK-603", name="Vrapčište", type_="Municipality"),
        MKSubdivision(code="MK-604", name="Gostivar", type_="Municipality"),
        MKSubdivision(code="MK-605", name="Želino", type_="Municipality"),
        MKSubdivision(code="MK-606", name="Jegunovce", type_="Municipality"),
        MKSubdivision(code="MK-607", name="Mavrovo i Rostuše", type_="Municipality"),
        MKSubdivision(code="MK-608", name="Tearce", type_="Municipality"),
        MKSubdivision(code="MK-609", name="Tetovo", type_="Municipality"),
        MKSubdivision(code="MK-701", name="Kratovo", type_="Municipality"),
        MKSubdivision(code="MK-702", name="Kriva Palanka", type_="Municipality"),
        MKSubdivision(code="MK-703", name="Kumanovo", type_="Municipality"),
        MKSubdivision(code="MK-704", name="Lipkovo", type_="Municipality"),
        MKSubdivision(code="MK-705", name="Rankovce", type_="Municipality"),
        MKSubdivision(code="MK-706", name="Staro Nagoričane", type_="Municipality"),
        MKSubdivision(code="MK-801", name="Aerodrom †", type_="Municipality"),
        MKSubdivision(code="MK-802", name="Aračinovo", type_="Municipality"),
        MKSubdivision(code="MK-803", name="Butel †", type_="Municipality"),
        MKSubdivision(code="MK-804", name="Gazi Baba †", type_="Municipality"),
        MKSubdivision(code="MK-805", name="Gjorče Petrov †", type_="Municipality"),
        MKSubdivision(code="MK-806", name="Zelenikovo", type_="Municipality"),
        MKSubdivision(code="MK-807", name="Ilinden", type_="Municipality"),
        MKSubdivision(code="MK-808", name="Karpoš †", type_="Municipality"),
        MKSubdivision(code="MK-809", name="Kisela Voda †", type_="Municipality"),
        MKSubdivision(code="MK-810", name="Petrovec", type_="Municipality"),
        MKSubdivision(code="MK-811", name="Saraj †", type_="Municipality"),
        MKSubdivision(code="MK-812", name="Sopište", type_="Municipality"),
        MKSubdivision(code="MK-813", name="Studeničani", type_="Municipality"),
        MKSubdivision(code="MK-814", name="Centar †", type_="Municipality"),
        MKSubdivision(code="MK-815", name="Čair †", type_="Municipality"),
        MKSubdivision(code="MK-816", name="Čučer-Sandevo", type_="Municipality"),
        MKSubdivision(code="MK-817", name="Šuto Orizari †", type_="Municipality"),
    ],
)
