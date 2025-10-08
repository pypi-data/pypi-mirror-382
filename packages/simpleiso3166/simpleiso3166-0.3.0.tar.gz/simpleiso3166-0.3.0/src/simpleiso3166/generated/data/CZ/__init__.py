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

CZSubdivisionCodeType = Literal[
    "CZ-10",  # Praha, Hlavní město
    "CZ-20",  # Středočeský kraj
    "CZ-201",  # Benešov
    "CZ-202",  # Beroun
    "CZ-203",  # Kladno
    "CZ-204",  # Kolín
    "CZ-205",  # Kutná Hora
    "CZ-206",  # Mělník
    "CZ-207",  # Mladá Boleslav
    "CZ-208",  # Nymburk
    "CZ-209",  # Praha-východ
    "CZ-20A",  # Praha-západ
    "CZ-20B",  # Příbram
    "CZ-20C",  # Rakovník
    "CZ-31",  # Jihočeský kraj
    "CZ-311",  # České Budějovice
    "CZ-312",  # Český Krumlov
    "CZ-313",  # Jindřichův Hradec
    "CZ-314",  # Písek
    "CZ-315",  # Prachatice
    "CZ-316",  # Strakonice
    "CZ-317",  # Tábor
    "CZ-32",  # Plzeňský kraj
    "CZ-321",  # Domažlice
    "CZ-322",  # Klatovy
    "CZ-323",  # Plzeň-město
    "CZ-324",  # Plzeň-jih
    "CZ-325",  # Plzeň-sever
    "CZ-326",  # Rokycany
    "CZ-327",  # Tachov
    "CZ-41",  # Karlovarský kraj
    "CZ-411",  # Cheb
    "CZ-412",  # Karlovy Vary
    "CZ-413",  # Sokolov
    "CZ-42",  # Ústecký kraj
    "CZ-421",  # Děčín
    "CZ-422",  # Chomutov
    "CZ-423",  # Litoměřice
    "CZ-424",  # Louny
    "CZ-425",  # Most
    "CZ-426",  # Teplice
    "CZ-427",  # Ústí nad Labem
    "CZ-51",  # Liberecký kraj
    "CZ-511",  # Česká Lípa
    "CZ-512",  # Jablonec nad Nisou
    "CZ-513",  # Liberec
    "CZ-514",  # Semily
    "CZ-52",  # Královéhradecký kraj
    "CZ-521",  # Hradec Králové
    "CZ-522",  # Jičín
    "CZ-523",  # Náchod
    "CZ-524",  # Rychnov nad Kněžnou
    "CZ-525",  # Trutnov
    "CZ-53",  # Pardubický kraj
    "CZ-531",  # Chrudim
    "CZ-532",  # Pardubice
    "CZ-533",  # Svitavy
    "CZ-534",  # Ústí nad Orlicí
    "CZ-63",  # Kraj Vysočina
    "CZ-631",  # Havlíčkův Brod
    "CZ-632",  # Jihlava
    "CZ-633",  # Pelhřimov
    "CZ-634",  # Třebíč
    "CZ-635",  # Žďár nad Sázavou
    "CZ-64",  # Jihomoravský kraj
    "CZ-641",  # Blansko
    "CZ-642",  # Brno-město
    "CZ-643",  # Brno-venkov
    "CZ-644",  # Břeclav
    "CZ-645",  # Hodonín
    "CZ-646",  # Vyškov
    "CZ-647",  # Znojmo
    "CZ-71",  # Olomoucký kraj
    "CZ-711",  # Jeseník
    "CZ-712",  # Olomouc
    "CZ-713",  # Prostějov
    "CZ-714",  # Přerov
    "CZ-715",  # Šumperk
    "CZ-72",  # Zlínský kraj
    "CZ-721",  # Kroměříž
    "CZ-722",  # Uherské Hradiště
    "CZ-723",  # Vsetín
    "CZ-724",  # Zlín
    "CZ-80",  # Moravskoslezský kraj
    "CZ-801",  # Bruntál
    "CZ-802",  # Frýdek-Místek
    "CZ-803",  # Karviná
    "CZ-804",  # Nový Jičín
    "CZ-805",  # Opava
    "CZ-806",  # Ostrava-město
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class CZSubdivision(Subdivision):
    code: CZSubdivisionCodeType


CZ: Final[Country] = Country(
    alpha2="CZ",
    alpha3="CZE",
    name="Czechia",
    common_name=None,
    official_name="Czech Republic",
    subdivisions=[
        CZSubdivision(code="CZ-10", name="Praha, Hlavní město", type_="Capital city"),
        CZSubdivision(code="CZ-20", name="Středočeský kraj", type_="Region"),
        CZSubdivision(code="CZ-201", name="Benešov", type_="District"),
        CZSubdivision(code="CZ-202", name="Beroun", type_="District"),
        CZSubdivision(code="CZ-203", name="Kladno", type_="District"),
        CZSubdivision(code="CZ-204", name="Kolín", type_="District"),
        CZSubdivision(code="CZ-205", name="Kutná Hora", type_="District"),
        CZSubdivision(code="CZ-206", name="Mělník", type_="District"),
        CZSubdivision(code="CZ-207", name="Mladá Boleslav", type_="District"),
        CZSubdivision(code="CZ-208", name="Nymburk", type_="District"),
        CZSubdivision(code="CZ-209", name="Praha-východ", type_="District"),
        CZSubdivision(code="CZ-20A", name="Praha-západ", type_="District"),
        CZSubdivision(code="CZ-20B", name="Příbram", type_="District"),
        CZSubdivision(code="CZ-20C", name="Rakovník", type_="District"),
        CZSubdivision(code="CZ-31", name="Jihočeský kraj", type_="Region"),
        CZSubdivision(code="CZ-311", name="České Budějovice", type_="District"),
        CZSubdivision(code="CZ-312", name="Český Krumlov", type_="District"),
        CZSubdivision(code="CZ-313", name="Jindřichův Hradec", type_="District"),
        CZSubdivision(code="CZ-314", name="Písek", type_="District"),
        CZSubdivision(code="CZ-315", name="Prachatice", type_="District"),
        CZSubdivision(code="CZ-316", name="Strakonice", type_="District"),
        CZSubdivision(code="CZ-317", name="Tábor", type_="District"),
        CZSubdivision(code="CZ-32", name="Plzeňský kraj", type_="Region"),
        CZSubdivision(code="CZ-321", name="Domažlice", type_="District"),
        CZSubdivision(code="CZ-322", name="Klatovy", type_="District"),
        CZSubdivision(code="CZ-323", name="Plzeň-město", type_="District"),
        CZSubdivision(code="CZ-324", name="Plzeň-jih", type_="District"),
        CZSubdivision(code="CZ-325", name="Plzeň-sever", type_="District"),
        CZSubdivision(code="CZ-326", name="Rokycany", type_="District"),
        CZSubdivision(code="CZ-327", name="Tachov", type_="District"),
        CZSubdivision(code="CZ-41", name="Karlovarský kraj", type_="Region"),
        CZSubdivision(code="CZ-411", name="Cheb", type_="District"),
        CZSubdivision(code="CZ-412", name="Karlovy Vary", type_="District"),
        CZSubdivision(code="CZ-413", name="Sokolov", type_="District"),
        CZSubdivision(code="CZ-42", name="Ústecký kraj", type_="Region"),
        CZSubdivision(code="CZ-421", name="Děčín", type_="District"),
        CZSubdivision(code="CZ-422", name="Chomutov", type_="District"),
        CZSubdivision(code="CZ-423", name="Litoměřice", type_="District"),
        CZSubdivision(code="CZ-424", name="Louny", type_="District"),
        CZSubdivision(code="CZ-425", name="Most", type_="District"),
        CZSubdivision(code="CZ-426", name="Teplice", type_="District"),
        CZSubdivision(code="CZ-427", name="Ústí nad Labem", type_="District"),
        CZSubdivision(code="CZ-51", name="Liberecký kraj", type_="Region"),
        CZSubdivision(code="CZ-511", name="Česká Lípa", type_="District"),
        CZSubdivision(code="CZ-512", name="Jablonec nad Nisou", type_="District"),
        CZSubdivision(code="CZ-513", name="Liberec", type_="District"),
        CZSubdivision(code="CZ-514", name="Semily", type_="District"),
        CZSubdivision(code="CZ-52", name="Královéhradecký kraj", type_="Region"),
        CZSubdivision(code="CZ-521", name="Hradec Králové", type_="District"),
        CZSubdivision(code="CZ-522", name="Jičín", type_="District"),
        CZSubdivision(code="CZ-523", name="Náchod", type_="District"),
        CZSubdivision(code="CZ-524", name="Rychnov nad Kněžnou", type_="District"),
        CZSubdivision(code="CZ-525", name="Trutnov", type_="District"),
        CZSubdivision(code="CZ-53", name="Pardubický kraj", type_="Region"),
        CZSubdivision(code="CZ-531", name="Chrudim", type_="District"),
        CZSubdivision(code="CZ-532", name="Pardubice", type_="District"),
        CZSubdivision(code="CZ-533", name="Svitavy", type_="District"),
        CZSubdivision(code="CZ-534", name="Ústí nad Orlicí", type_="District"),
        CZSubdivision(code="CZ-63", name="Kraj Vysočina", type_="Region"),
        CZSubdivision(code="CZ-631", name="Havlíčkův Brod", type_="District"),
        CZSubdivision(code="CZ-632", name="Jihlava", type_="District"),
        CZSubdivision(code="CZ-633", name="Pelhřimov", type_="District"),
        CZSubdivision(code="CZ-634", name="Třebíč", type_="District"),
        CZSubdivision(code="CZ-635", name="Žďár nad Sázavou", type_="District"),
        CZSubdivision(code="CZ-64", name="Jihomoravský kraj", type_="Region"),
        CZSubdivision(code="CZ-641", name="Blansko", type_="District"),
        CZSubdivision(code="CZ-642", name="Brno-město", type_="District"),
        CZSubdivision(code="CZ-643", name="Brno-venkov", type_="District"),
        CZSubdivision(code="CZ-644", name="Břeclav", type_="District"),
        CZSubdivision(code="CZ-645", name="Hodonín", type_="District"),
        CZSubdivision(code="CZ-646", name="Vyškov", type_="District"),
        CZSubdivision(code="CZ-647", name="Znojmo", type_="District"),
        CZSubdivision(code="CZ-71", name="Olomoucký kraj", type_="Region"),
        CZSubdivision(code="CZ-711", name="Jeseník", type_="District"),
        CZSubdivision(code="CZ-712", name="Olomouc", type_="District"),
        CZSubdivision(code="CZ-713", name="Prostějov", type_="District"),
        CZSubdivision(code="CZ-714", name="Přerov", type_="District"),
        CZSubdivision(code="CZ-715", name="Šumperk", type_="District"),
        CZSubdivision(code="CZ-72", name="Zlínský kraj", type_="Region"),
        CZSubdivision(code="CZ-721", name="Kroměříž", type_="District"),
        CZSubdivision(code="CZ-722", name="Uherské Hradiště", type_="District"),
        CZSubdivision(code="CZ-723", name="Vsetín", type_="District"),
        CZSubdivision(code="CZ-724", name="Zlín", type_="District"),
        CZSubdivision(code="CZ-80", name="Moravskoslezský kraj", type_="Region"),
        CZSubdivision(code="CZ-801", name="Bruntál", type_="District"),
        CZSubdivision(code="CZ-802", name="Frýdek-Místek", type_="District"),
        CZSubdivision(code="CZ-803", name="Karviná", type_="District"),
        CZSubdivision(code="CZ-804", name="Nový Jičín", type_="District"),
        CZSubdivision(code="CZ-805", name="Opava", type_="District"),
        CZSubdivision(code="CZ-806", name="Ostrava-město", type_="District"),
    ],
)
