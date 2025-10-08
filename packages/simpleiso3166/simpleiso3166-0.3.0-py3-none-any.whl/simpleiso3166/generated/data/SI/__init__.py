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

SISubdivisionCodeType = Literal[
    "SI-001",  # Ajdovščina
    "SI-002",  # Beltinci
    "SI-003",  # Bled
    "SI-004",  # Bohinj
    "SI-005",  # Borovnica
    "SI-006",  # Bovec
    "SI-007",  # Brda
    "SI-008",  # Brezovica
    "SI-009",  # Brežice
    "SI-010",  # Tišina
    "SI-011",  # Celje
    "SI-012",  # Cerklje na Gorenjskem
    "SI-013",  # Cerknica
    "SI-014",  # Cerkno
    "SI-015",  # Črenšovci
    "SI-016",  # Črna na Koroškem
    "SI-017",  # Črnomelj
    "SI-018",  # Destrnik
    "SI-019",  # Divača
    "SI-020",  # Dobrepolje
    "SI-021",  # Dobrova-Polhov Gradec
    "SI-022",  # Dol pri Ljubljani
    "SI-023",  # Domžale
    "SI-024",  # Dornava
    "SI-025",  # Dravograd
    "SI-026",  # Duplek
    "SI-027",  # Gorenja vas-Poljane
    "SI-028",  # Gorišnica
    "SI-029",  # Gornja Radgona
    "SI-030",  # Gornji Grad
    "SI-031",  # Gornji Petrovci
    "SI-032",  # Grosuplje
    "SI-033",  # Šalovci
    "SI-034",  # Hrastnik
    "SI-035",  # Hrpelje-Kozina
    "SI-036",  # Idrija
    "SI-037",  # Ig
    "SI-038",  # Ilirska Bistrica
    "SI-039",  # Ivančna Gorica
    "SI-040",  # Izola
    "SI-041",  # Jesenice
    "SI-042",  # Juršinci
    "SI-043",  # Kamnik
    "SI-044",  # Kanal ob Soči
    "SI-045",  # Kidričevo
    "SI-046",  # Kobarid
    "SI-047",  # Kobilje
    "SI-048",  # Kočevje
    "SI-049",  # Komen
    "SI-050",  # Koper
    "SI-051",  # Kozje
    "SI-052",  # Kranj
    "SI-053",  # Kranjska Gora
    "SI-054",  # Krško
    "SI-055",  # Kungota
    "SI-056",  # Kuzma
    "SI-057",  # Laško
    "SI-058",  # Lenart
    "SI-059",  # Lendava
    "SI-060",  # Litija
    "SI-061",  # Ljubljana
    "SI-062",  # Ljubno
    "SI-063",  # Ljutomer
    "SI-064",  # Logatec
    "SI-065",  # Loška dolina
    "SI-066",  # Loški Potok
    "SI-067",  # Luče
    "SI-068",  # Lukovica
    "SI-069",  # Majšperk
    "SI-070",  # Maribor
    "SI-071",  # Medvode
    "SI-072",  # Mengeš
    "SI-073",  # Metlika
    "SI-074",  # Mežica
    "SI-075",  # Miren-Kostanjevica
    "SI-076",  # Mislinja
    "SI-077",  # Moravče
    "SI-078",  # Moravske Toplice
    "SI-079",  # Mozirje
    "SI-080",  # Murska Sobota
    "SI-081",  # Muta
    "SI-082",  # Naklo
    "SI-083",  # Nazarje
    "SI-084",  # Nova Gorica
    "SI-085",  # Novo Mesto
    "SI-086",  # Odranci
    "SI-087",  # Ormož
    "SI-088",  # Osilnica
    "SI-089",  # Pesnica
    "SI-090",  # Piran
    "SI-091",  # Pivka
    "SI-092",  # Podčetrtek
    "SI-093",  # Podvelka
    "SI-094",  # Postojna
    "SI-095",  # Preddvor
    "SI-096",  # Ptuj
    "SI-097",  # Puconci
    "SI-098",  # Rače-Fram
    "SI-099",  # Radeče
    "SI-100",  # Radenci
    "SI-101",  # Radlje ob Dravi
    "SI-102",  # Radovljica
    "SI-103",  # Ravne na Koroškem
    "SI-104",  # Ribnica
    "SI-105",  # Rogašovci
    "SI-106",  # Rogaška Slatina
    "SI-107",  # Rogatec
    "SI-108",  # Ruše
    "SI-109",  # Semič
    "SI-110",  # Sevnica
    "SI-111",  # Sežana
    "SI-112",  # Slovenj Gradec
    "SI-113",  # Slovenska Bistrica
    "SI-114",  # Slovenske Konjice
    "SI-115",  # Starše
    "SI-116",  # Sveti Jurij ob Ščavnici
    "SI-117",  # Šenčur
    "SI-118",  # Šentilj
    "SI-119",  # Šentjernej
    "SI-120",  # Šentjur
    "SI-121",  # Škocjan
    "SI-122",  # Škofja Loka
    "SI-123",  # Škofljica
    "SI-124",  # Šmarje pri Jelšah
    "SI-125",  # Šmartno ob Paki
    "SI-126",  # Šoštanj
    "SI-127",  # Štore
    "SI-128",  # Tolmin
    "SI-129",  # Trbovlje
    "SI-130",  # Trebnje
    "SI-131",  # Tržič
    "SI-132",  # Turnišče
    "SI-133",  # Velenje
    "SI-134",  # Velike Lašče
    "SI-135",  # Videm
    "SI-136",  # Vipava
    "SI-137",  # Vitanje
    "SI-138",  # Vodice
    "SI-139",  # Vojnik
    "SI-140",  # Vrhnika
    "SI-141",  # Vuzenica
    "SI-142",  # Zagorje ob Savi
    "SI-143",  # Zavrč
    "SI-144",  # Zreče
    "SI-146",  # Železniki
    "SI-147",  # Žiri
    "SI-148",  # Benedikt
    "SI-149",  # Bistrica ob Sotli
    "SI-150",  # Bloke
    "SI-151",  # Braslovče
    "SI-152",  # Cankova
    "SI-153",  # Cerkvenjak
    "SI-154",  # Dobje
    "SI-155",  # Dobrna
    "SI-156",  # Dobrovnik
    "SI-157",  # Dolenjske Toplice
    "SI-158",  # Grad
    "SI-159",  # Hajdina
    "SI-160",  # Hoče-Slivnica
    "SI-161",  # Hodoš
    "SI-162",  # Horjul
    "SI-163",  # Jezersko
    "SI-164",  # Komenda
    "SI-165",  # Kostel
    "SI-166",  # Križevci
    "SI-167",  # Lovrenc na Pohorju
    "SI-168",  # Markovci
    "SI-169",  # Miklavž na Dravskem polju
    "SI-170",  # Mirna Peč
    "SI-171",  # Oplotnica
    "SI-172",  # Podlehnik
    "SI-173",  # Polzela
    "SI-174",  # Prebold
    "SI-175",  # Prevalje
    "SI-176",  # Razkrižje
    "SI-177",  # Ribnica na Pohorju
    "SI-178",  # Selnica ob Dravi
    "SI-179",  # Sodražica
    "SI-180",  # Solčava
    "SI-181",  # Sveta Ana
    "SI-182",  # Sveti Andraž v Slovenskih goricah
    "SI-183",  # Šempeter-Vrtojba
    "SI-184",  # Tabor
    "SI-185",  # Trnovska Vas
    "SI-186",  # Trzin
    "SI-187",  # Velika Polana
    "SI-188",  # Veržej
    "SI-189",  # Vransko
    "SI-190",  # Žalec
    "SI-191",  # Žetale
    "SI-192",  # Žirovnica
    "SI-193",  # Žužemberk
    "SI-194",  # Šmartno pri Litiji
    "SI-195",  # Apače
    "SI-196",  # Cirkulane
    "SI-197",  # Kostanjevica na Krki
    "SI-198",  # Makole
    "SI-199",  # Mokronog-Trebelno
    "SI-200",  # Poljčane
    "SI-201",  # Renče-Vogrsko
    "SI-202",  # Središče ob Dravi
    "SI-203",  # Straža
    "SI-204",  # Sveta Trojica v Slovenskih goricah
    "SI-205",  # Sveti Tomaž
    "SI-206",  # Šmarješke Toplice
    "SI-207",  # Gorje
    "SI-208",  # Log-Dragomer
    "SI-209",  # Rečica ob Savinji
    "SI-210",  # Sveti Jurij v Slovenskih goricah
    "SI-211",  # Šentrupert
    "SI-212",  # Mirna
    "SI-213",  # Ankaran
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SISubdivision(Subdivision):
    code: SISubdivisionCodeType


SI: Final[Country] = Country(
    alpha2="SI",
    alpha3="SVN",
    name="Slovenia",
    common_name=None,
    official_name="Republic of Slovenia",
    subdivisions=[
        SISubdivision(code="SI-001", name="Ajdovščina", type_="Municipality"),
        SISubdivision(code="SI-002", name="Beltinci", type_="Municipality"),
        SISubdivision(code="SI-003", name="Bled", type_="Municipality"),
        SISubdivision(code="SI-004", name="Bohinj", type_="Municipality"),
        SISubdivision(code="SI-005", name="Borovnica", type_="Municipality"),
        SISubdivision(code="SI-006", name="Bovec", type_="Municipality"),
        SISubdivision(code="SI-007", name="Brda", type_="Municipality"),
        SISubdivision(code="SI-008", name="Brezovica", type_="Municipality"),
        SISubdivision(code="SI-009", name="Brežice", type_="Municipality"),
        SISubdivision(code="SI-010", name="Tišina", type_="Municipality"),
        SISubdivision(code="SI-011", name="Celje", type_="Urban municipality"),
        SISubdivision(code="SI-012", name="Cerklje na Gorenjskem", type_="Municipality"),
        SISubdivision(code="SI-013", name="Cerknica", type_="Municipality"),
        SISubdivision(code="SI-014", name="Cerkno", type_="Municipality"),
        SISubdivision(code="SI-015", name="Črenšovci", type_="Municipality"),
        SISubdivision(code="SI-016", name="Črna na Koroškem", type_="Municipality"),
        SISubdivision(code="SI-017", name="Črnomelj", type_="Municipality"),
        SISubdivision(code="SI-018", name="Destrnik", type_="Municipality"),
        SISubdivision(code="SI-019", name="Divača", type_="Municipality"),
        SISubdivision(code="SI-020", name="Dobrepolje", type_="Municipality"),
        SISubdivision(code="SI-021", name="Dobrova-Polhov Gradec", type_="Municipality"),
        SISubdivision(code="SI-022", name="Dol pri Ljubljani", type_="Municipality"),
        SISubdivision(code="SI-023", name="Domžale", type_="Municipality"),
        SISubdivision(code="SI-024", name="Dornava", type_="Municipality"),
        SISubdivision(code="SI-025", name="Dravograd", type_="Municipality"),
        SISubdivision(code="SI-026", name="Duplek", type_="Municipality"),
        SISubdivision(code="SI-027", name="Gorenja vas-Poljane", type_="Municipality"),
        SISubdivision(code="SI-028", name="Gorišnica", type_="Municipality"),
        SISubdivision(code="SI-029", name="Gornja Radgona", type_="Municipality"),
        SISubdivision(code="SI-030", name="Gornji Grad", type_="Municipality"),
        SISubdivision(code="SI-031", name="Gornji Petrovci", type_="Municipality"),
        SISubdivision(code="SI-032", name="Grosuplje", type_="Municipality"),
        SISubdivision(code="SI-033", name="Šalovci", type_="Municipality"),
        SISubdivision(code="SI-034", name="Hrastnik", type_="Municipality"),
        SISubdivision(code="SI-035", name="Hrpelje-Kozina", type_="Municipality"),
        SISubdivision(code="SI-036", name="Idrija", type_="Municipality"),
        SISubdivision(code="SI-037", name="Ig", type_="Municipality"),
        SISubdivision(code="SI-038", name="Ilirska Bistrica", type_="Municipality"),
        SISubdivision(code="SI-039", name="Ivančna Gorica", type_="Municipality"),
        SISubdivision(code="SI-040", name="Izola", type_="Municipality"),
        SISubdivision(code="SI-041", name="Jesenice", type_="Municipality"),
        SISubdivision(code="SI-042", name="Juršinci", type_="Municipality"),
        SISubdivision(code="SI-043", name="Kamnik", type_="Municipality"),
        SISubdivision(code="SI-044", name="Kanal ob Soči", type_="Municipality"),
        SISubdivision(code="SI-045", name="Kidričevo", type_="Municipality"),
        SISubdivision(code="SI-046", name="Kobarid", type_="Municipality"),
        SISubdivision(code="SI-047", name="Kobilje", type_="Municipality"),
        SISubdivision(code="SI-048", name="Kočevje", type_="Municipality"),
        SISubdivision(code="SI-049", name="Komen", type_="Municipality"),
        SISubdivision(code="SI-050", name="Koper", type_="Urban municipality"),
        SISubdivision(code="SI-051", name="Kozje", type_="Municipality"),
        SISubdivision(code="SI-052", name="Kranj", type_="Urban municipality"),
        SISubdivision(code="SI-053", name="Kranjska Gora", type_="Municipality"),
        SISubdivision(code="SI-054", name="Krško", type_="Urban municipality"),
        SISubdivision(code="SI-055", name="Kungota", type_="Municipality"),
        SISubdivision(code="SI-056", name="Kuzma", type_="Municipality"),
        SISubdivision(code="SI-057", name="Laško", type_="Municipality"),
        SISubdivision(code="SI-058", name="Lenart", type_="Municipality"),
        SISubdivision(code="SI-059", name="Lendava", type_="Municipality"),
        SISubdivision(code="SI-060", name="Litija", type_="Municipality"),
        SISubdivision(code="SI-061", name="Ljubljana", type_="Urban municipality"),
        SISubdivision(code="SI-062", name="Ljubno", type_="Municipality"),
        SISubdivision(code="SI-063", name="Ljutomer", type_="Municipality"),
        SISubdivision(code="SI-064", name="Logatec", type_="Municipality"),
        SISubdivision(code="SI-065", name="Loška dolina", type_="Municipality"),
        SISubdivision(code="SI-066", name="Loški Potok", type_="Municipality"),
        SISubdivision(code="SI-067", name="Luče", type_="Municipality"),
        SISubdivision(code="SI-068", name="Lukovica", type_="Municipality"),
        SISubdivision(code="SI-069", name="Majšperk", type_="Municipality"),
        SISubdivision(code="SI-070", name="Maribor", type_="Urban municipality"),
        SISubdivision(code="SI-071", name="Medvode", type_="Municipality"),
        SISubdivision(code="SI-072", name="Mengeš", type_="Municipality"),
        SISubdivision(code="SI-073", name="Metlika", type_="Municipality"),
        SISubdivision(code="SI-074", name="Mežica", type_="Municipality"),
        SISubdivision(code="SI-075", name="Miren-Kostanjevica", type_="Municipality"),
        SISubdivision(code="SI-076", name="Mislinja", type_="Municipality"),
        SISubdivision(code="SI-077", name="Moravče", type_="Municipality"),
        SISubdivision(code="SI-078", name="Moravske Toplice", type_="Municipality"),
        SISubdivision(code="SI-079", name="Mozirje", type_="Municipality"),
        SISubdivision(code="SI-080", name="Murska Sobota", type_="Urban municipality"),
        SISubdivision(code="SI-081", name="Muta", type_="Municipality"),
        SISubdivision(code="SI-082", name="Naklo", type_="Municipality"),
        SISubdivision(code="SI-083", name="Nazarje", type_="Municipality"),
        SISubdivision(code="SI-084", name="Nova Gorica", type_="Urban municipality"),
        SISubdivision(code="SI-085", name="Novo Mesto", type_="Urban municipality"),
        SISubdivision(code="SI-086", name="Odranci", type_="Municipality"),
        SISubdivision(code="SI-087", name="Ormož", type_="Municipality"),
        SISubdivision(code="SI-088", name="Osilnica", type_="Municipality"),
        SISubdivision(code="SI-089", name="Pesnica", type_="Municipality"),
        SISubdivision(code="SI-090", name="Piran", type_="Municipality"),
        SISubdivision(code="SI-091", name="Pivka", type_="Municipality"),
        SISubdivision(code="SI-092", name="Podčetrtek", type_="Municipality"),
        SISubdivision(code="SI-093", name="Podvelka", type_="Municipality"),
        SISubdivision(code="SI-094", name="Postojna", type_="Municipality"),
        SISubdivision(code="SI-095", name="Preddvor", type_="Municipality"),
        SISubdivision(code="SI-096", name="Ptuj", type_="Urban municipality"),
        SISubdivision(code="SI-097", name="Puconci", type_="Municipality"),
        SISubdivision(code="SI-098", name="Rače-Fram", type_="Municipality"),
        SISubdivision(code="SI-099", name="Radeče", type_="Municipality"),
        SISubdivision(code="SI-100", name="Radenci", type_="Municipality"),
        SISubdivision(code="SI-101", name="Radlje ob Dravi", type_="Municipality"),
        SISubdivision(code="SI-102", name="Radovljica", type_="Municipality"),
        SISubdivision(code="SI-103", name="Ravne na Koroškem", type_="Municipality"),
        SISubdivision(code="SI-104", name="Ribnica", type_="Municipality"),
        SISubdivision(code="SI-105", name="Rogašovci", type_="Municipality"),
        SISubdivision(code="SI-106", name="Rogaška Slatina", type_="Municipality"),
        SISubdivision(code="SI-107", name="Rogatec", type_="Municipality"),
        SISubdivision(code="SI-108", name="Ruše", type_="Municipality"),
        SISubdivision(code="SI-109", name="Semič", type_="Municipality"),
        SISubdivision(code="SI-110", name="Sevnica", type_="Municipality"),
        SISubdivision(code="SI-111", name="Sežana", type_="Municipality"),
        SISubdivision(code="SI-112", name="Slovenj Gradec", type_="Urban municipality"),
        SISubdivision(code="SI-113", name="Slovenska Bistrica", type_="Municipality"),
        SISubdivision(code="SI-114", name="Slovenske Konjice", type_="Municipality"),
        SISubdivision(code="SI-115", name="Starše", type_="Municipality"),
        SISubdivision(code="SI-116", name="Sveti Jurij ob Ščavnici", type_="Municipality"),
        SISubdivision(code="SI-117", name="Šenčur", type_="Municipality"),
        SISubdivision(code="SI-118", name="Šentilj", type_="Municipality"),
        SISubdivision(code="SI-119", name="Šentjernej", type_="Municipality"),
        SISubdivision(code="SI-120", name="Šentjur", type_="Municipality"),
        SISubdivision(code="SI-121", name="Škocjan", type_="Municipality"),
        SISubdivision(code="SI-122", name="Škofja Loka", type_="Municipality"),
        SISubdivision(code="SI-123", name="Škofljica", type_="Municipality"),
        SISubdivision(code="SI-124", name="Šmarje pri Jelšah", type_="Municipality"),
        SISubdivision(code="SI-125", name="Šmartno ob Paki", type_="Municipality"),
        SISubdivision(code="SI-126", name="Šoštanj", type_="Municipality"),
        SISubdivision(code="SI-127", name="Štore", type_="Municipality"),
        SISubdivision(code="SI-128", name="Tolmin", type_="Municipality"),
        SISubdivision(code="SI-129", name="Trbovlje", type_="Municipality"),
        SISubdivision(code="SI-130", name="Trebnje", type_="Municipality"),
        SISubdivision(code="SI-131", name="Tržič", type_="Municipality"),
        SISubdivision(code="SI-132", name="Turnišče", type_="Municipality"),
        SISubdivision(code="SI-133", name="Velenje", type_="Urban municipality"),
        SISubdivision(code="SI-134", name="Velike Lašče", type_="Municipality"),
        SISubdivision(code="SI-135", name="Videm", type_="Municipality"),
        SISubdivision(code="SI-136", name="Vipava", type_="Municipality"),
        SISubdivision(code="SI-137", name="Vitanje", type_="Municipality"),
        SISubdivision(code="SI-138", name="Vodice", type_="Municipality"),
        SISubdivision(code="SI-139", name="Vojnik", type_="Municipality"),
        SISubdivision(code="SI-140", name="Vrhnika", type_="Municipality"),
        SISubdivision(code="SI-141", name="Vuzenica", type_="Municipality"),
        SISubdivision(code="SI-142", name="Zagorje ob Savi", type_="Municipality"),
        SISubdivision(code="SI-143", name="Zavrč", type_="Municipality"),
        SISubdivision(code="SI-144", name="Zreče", type_="Municipality"),
        SISubdivision(code="SI-146", name="Železniki", type_="Municipality"),
        SISubdivision(code="SI-147", name="Žiri", type_="Municipality"),
        SISubdivision(code="SI-148", name="Benedikt", type_="Municipality"),
        SISubdivision(code="SI-149", name="Bistrica ob Sotli", type_="Municipality"),
        SISubdivision(code="SI-150", name="Bloke", type_="Municipality"),
        SISubdivision(code="SI-151", name="Braslovče", type_="Municipality"),
        SISubdivision(code="SI-152", name="Cankova", type_="Municipality"),
        SISubdivision(code="SI-153", name="Cerkvenjak", type_="Municipality"),
        SISubdivision(code="SI-154", name="Dobje", type_="Municipality"),
        SISubdivision(code="SI-155", name="Dobrna", type_="Municipality"),
        SISubdivision(code="SI-156", name="Dobrovnik", type_="Municipality"),
        SISubdivision(code="SI-157", name="Dolenjske Toplice", type_="Municipality"),
        SISubdivision(code="SI-158", name="Grad", type_="Municipality"),
        SISubdivision(code="SI-159", name="Hajdina", type_="Municipality"),
        SISubdivision(code="SI-160", name="Hoče-Slivnica", type_="Municipality"),
        SISubdivision(code="SI-161", name="Hodoš", type_="Municipality"),
        SISubdivision(code="SI-162", name="Horjul", type_="Municipality"),
        SISubdivision(code="SI-163", name="Jezersko", type_="Municipality"),
        SISubdivision(code="SI-164", name="Komenda", type_="Municipality"),
        SISubdivision(code="SI-165", name="Kostel", type_="Municipality"),
        SISubdivision(code="SI-166", name="Križevci", type_="Municipality"),
        SISubdivision(code="SI-167", name="Lovrenc na Pohorju", type_="Municipality"),
        SISubdivision(code="SI-168", name="Markovci", type_="Municipality"),
        SISubdivision(code="SI-169", name="Miklavž na Dravskem polju", type_="Municipality"),
        SISubdivision(code="SI-170", name="Mirna Peč", type_="Municipality"),
        SISubdivision(code="SI-171", name="Oplotnica", type_="Municipality"),
        SISubdivision(code="SI-172", name="Podlehnik", type_="Municipality"),
        SISubdivision(code="SI-173", name="Polzela", type_="Municipality"),
        SISubdivision(code="SI-174", name="Prebold", type_="Municipality"),
        SISubdivision(code="SI-175", name="Prevalje", type_="Municipality"),
        SISubdivision(code="SI-176", name="Razkrižje", type_="Municipality"),
        SISubdivision(code="SI-177", name="Ribnica na Pohorju", type_="Municipality"),
        SISubdivision(code="SI-178", name="Selnica ob Dravi", type_="Municipality"),
        SISubdivision(code="SI-179", name="Sodražica", type_="Municipality"),
        SISubdivision(code="SI-180", name="Solčava", type_="Municipality"),
        SISubdivision(code="SI-181", name="Sveta Ana", type_="Municipality"),
        SISubdivision(code="SI-182", name="Sveti Andraž v Slovenskih goricah", type_="Municipality"),
        SISubdivision(code="SI-183", name="Šempeter-Vrtojba", type_="Municipality"),
        SISubdivision(code="SI-184", name="Tabor", type_="Municipality"),
        SISubdivision(code="SI-185", name="Trnovska Vas", type_="Municipality"),
        SISubdivision(code="SI-186", name="Trzin", type_="Municipality"),
        SISubdivision(code="SI-187", name="Velika Polana", type_="Municipality"),
        SISubdivision(code="SI-188", name="Veržej", type_="Municipality"),
        SISubdivision(code="SI-189", name="Vransko", type_="Municipality"),
        SISubdivision(code="SI-190", name="Žalec", type_="Municipality"),
        SISubdivision(code="SI-191", name="Žetale", type_="Municipality"),
        SISubdivision(code="SI-192", name="Žirovnica", type_="Municipality"),
        SISubdivision(code="SI-193", name="Žužemberk", type_="Municipality"),
        SISubdivision(code="SI-194", name="Šmartno pri Litiji", type_="Municipality"),
        SISubdivision(code="SI-195", name="Apače", type_="Municipality"),
        SISubdivision(code="SI-196", name="Cirkulane", type_="Municipality"),
        SISubdivision(code="SI-197", name="Kostanjevica na Krki", type_="Municipality"),
        SISubdivision(code="SI-198", name="Makole", type_="Municipality"),
        SISubdivision(code="SI-199", name="Mokronog-Trebelno", type_="Municipality"),
        SISubdivision(code="SI-200", name="Poljčane", type_="Municipality"),
        SISubdivision(code="SI-201", name="Renče-Vogrsko", type_="Municipality"),
        SISubdivision(code="SI-202", name="Središče ob Dravi", type_="Municipality"),
        SISubdivision(code="SI-203", name="Straža", type_="Municipality"),
        SISubdivision(code="SI-204", name="Sveta Trojica v Slovenskih goricah", type_="Municipality"),
        SISubdivision(code="SI-205", name="Sveti Tomaž", type_="Municipality"),
        SISubdivision(code="SI-206", name="Šmarješke Toplice", type_="Municipality"),
        SISubdivision(code="SI-207", name="Gorje", type_="Municipality"),
        SISubdivision(code="SI-208", name="Log-Dragomer", type_="Municipality"),
        SISubdivision(code="SI-209", name="Rečica ob Savinji", type_="Municipality"),
        SISubdivision(code="SI-210", name="Sveti Jurij v Slovenskih goricah", type_="Municipality"),
        SISubdivision(code="SI-211", name="Šentrupert", type_="Municipality"),
        SISubdivision(code="SI-212", name="Mirna", type_="Municipality"),
        SISubdivision(code="SI-213", name="Ankaran", type_="Municipality"),
    ],
)
