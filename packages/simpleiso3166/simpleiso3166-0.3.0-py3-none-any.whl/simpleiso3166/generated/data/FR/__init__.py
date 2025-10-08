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

FRSubdivisionCodeType = Literal[
    "FR-01",  # Ain
    "FR-02",  # Aisne
    "FR-03",  # Allier
    "FR-04",  # Alpes-de-Haute-Provence
    "FR-05",  # Hautes-Alpes
    "FR-06",  # Alpes-Maritimes
    "FR-07",  # Ardèche
    "FR-08",  # Ardennes
    "FR-09",  # Ariège
    "FR-10",  # Aube
    "FR-11",  # Aude
    "FR-12",  # Aveyron
    "FR-13",  # Bouches-du-Rhône
    "FR-14",  # Calvados
    "FR-15",  # Cantal
    "FR-16",  # Charente
    "FR-17",  # Charente-Maritime
    "FR-18",  # Cher
    "FR-19",  # Corrèze
    "FR-20R",  # Corse
    "FR-21",  # Côte-d'Or
    "FR-22",  # Côtes-d'Armor
    "FR-23",  # Creuse
    "FR-24",  # Dordogne
    "FR-25",  # Doubs
    "FR-26",  # Drôme
    "FR-27",  # Eure
    "FR-28",  # Eure-et-Loir
    "FR-29",  # Finistère
    "FR-2A",  # Corse-du-Sud
    "FR-2B",  # Haute-Corse
    "FR-30",  # Gard
    "FR-31",  # Haute-Garonne
    "FR-32",  # Gers
    "FR-33",  # Gironde
    "FR-34",  # Hérault
    "FR-35",  # Ille-et-Vilaine
    "FR-36",  # Indre
    "FR-37",  # Indre-et-Loire
    "FR-38",  # Isère
    "FR-39",  # Jura
    "FR-40",  # Landes
    "FR-41",  # Loir-et-Cher
    "FR-42",  # Loire
    "FR-43",  # Haute-Loire
    "FR-44",  # Loire-Atlantique
    "FR-45",  # Loiret
    "FR-46",  # Lot
    "FR-47",  # Lot-et-Garonne
    "FR-48",  # Lozère
    "FR-49",  # Maine-et-Loire
    "FR-50",  # Manche
    "FR-51",  # Marne
    "FR-52",  # Haute-Marne
    "FR-53",  # Mayenne
    "FR-54",  # Meurthe-et-Moselle
    "FR-55",  # Meuse
    "FR-56",  # Morbihan
    "FR-57",  # Moselle
    "FR-58",  # Nièvre
    "FR-59",  # Nord
    "FR-60",  # Oise
    "FR-61",  # Orne
    "FR-62",  # Pas-de-Calais
    "FR-63",  # Puy-de-Dôme
    "FR-64",  # Pyrénées-Atlantiques
    "FR-65",  # Hautes-Pyrénées
    "FR-66",  # Pyrénées-Orientales
    "FR-67",  # Bas-Rhin
    "FR-68",  # Haut-Rhin
    "FR-69",  # Rhône
    "FR-69M",  # Métropole de Lyon
    "FR-6AE",  # Alsace
    "FR-70",  # Haute-Saône
    "FR-71",  # Saône-et-Loire
    "FR-72",  # Sarthe
    "FR-73",  # Savoie
    "FR-74",  # Haute-Savoie
    "FR-75C",  # Paris
    "FR-76",  # Seine-Maritime
    "FR-77",  # Seine-et-Marne
    "FR-78",  # Yvelines
    "FR-79",  # Deux-Sèvres
    "FR-80",  # Somme
    "FR-81",  # Tarn
    "FR-82",  # Tarn-et-Garonne
    "FR-83",  # Var
    "FR-84",  # Vaucluse
    "FR-85",  # Vendée
    "FR-86",  # Vienne
    "FR-87",  # Haute-Vienne
    "FR-88",  # Vosges
    "FR-89",  # Yonne
    "FR-90",  # Territoire de Belfort
    "FR-91",  # Essonne
    "FR-92",  # Hauts-de-Seine
    "FR-93",  # Seine-Saint-Denis
    "FR-94",  # Val-de-Marne
    "FR-95",  # Val-d'Oise
    "FR-971",  # Guadeloupe
    "FR-972",  # Martinique
    "FR-973",  # Guyane (française)
    "FR-974",  # La Réunion
    "FR-976",  # Mayotte
    "FR-ARA",  # Auvergne-Rhône-Alpes
    "FR-BFC",  # Bourgogne-Franche-Comté
    "FR-BL",  # Saint-Barthélemy
    "FR-BRE",  # Bretagne
    "FR-CP",  # Clipperton
    "FR-CVL",  # Centre-Val de Loire
    "FR-GES",  # Grand-Est
    "FR-HDF",  # Hauts-de-France
    "FR-IDF",  # Île-de-France
    "FR-MF",  # Saint-Martin
    "FR-NAQ",  # Nouvelle-Aquitaine
    "FR-NC",  # Nouvelle-Calédonie
    "FR-NOR",  # Normandie
    "FR-OCC",  # Occitanie
    "FR-PAC",  # Provence-Alpes-Côte-d’Azur
    "FR-PDL",  # Pays-de-la-Loire
    "FR-PF",  # Polynésie française
    "FR-PM",  # Saint-Pierre-et-Miquelon
    "FR-TF",  # Terres australes françaises
    "FR-WF",  # Wallis-et-Futuna
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class FRSubdivision(Subdivision):
    code: FRSubdivisionCodeType


FR: Final[Country] = Country(
    alpha2="FR",
    alpha3="FRA",
    name="France",
    common_name=None,
    official_name="French Republic",
    subdivisions=[
        FRSubdivision(code="FR-01", name="Ain", type_="Metropolitan department"),
        FRSubdivision(code="FR-02", name="Aisne", type_="Metropolitan department"),
        FRSubdivision(code="FR-03", name="Allier", type_="Metropolitan department"),
        FRSubdivision(code="FR-04", name="Alpes-de-Haute-Provence", type_="Metropolitan department"),
        FRSubdivision(code="FR-05", name="Hautes-Alpes", type_="Metropolitan department"),
        FRSubdivision(code="FR-06", name="Alpes-Maritimes", type_="Metropolitan department"),
        FRSubdivision(code="FR-07", name="Ardèche", type_="Metropolitan department"),
        FRSubdivision(code="FR-08", name="Ardennes", type_="Metropolitan department"),
        FRSubdivision(code="FR-09", name="Ariège", type_="Metropolitan department"),
        FRSubdivision(code="FR-10", name="Aube", type_="Metropolitan department"),
        FRSubdivision(code="FR-11", name="Aude", type_="Metropolitan department"),
        FRSubdivision(code="FR-12", name="Aveyron", type_="Metropolitan department"),
        FRSubdivision(code="FR-13", name="Bouches-du-Rhône", type_="Metropolitan department"),
        FRSubdivision(code="FR-14", name="Calvados", type_="Metropolitan department"),
        FRSubdivision(code="FR-15", name="Cantal", type_="Metropolitan department"),
        FRSubdivision(code="FR-16", name="Charente", type_="Metropolitan department"),
        FRSubdivision(code="FR-17", name="Charente-Maritime", type_="Metropolitan department"),
        FRSubdivision(code="FR-18", name="Cher", type_="Metropolitan department"),
        FRSubdivision(code="FR-19", name="Corrèze", type_="Metropolitan department"),
        FRSubdivision(code="FR-20R", name="Corse", type_="Metropolitan collectivity with special status"),
        FRSubdivision(code="FR-21", name="Côte-d'Or", type_="Metropolitan department"),
        FRSubdivision(code="FR-22", name="Côtes-d'Armor", type_="Metropolitan department"),
        FRSubdivision(code="FR-23", name="Creuse", type_="Metropolitan department"),
        FRSubdivision(code="FR-24", name="Dordogne", type_="Metropolitan department"),
        FRSubdivision(code="FR-25", name="Doubs", type_="Metropolitan department"),
        FRSubdivision(code="FR-26", name="Drôme", type_="Metropolitan department"),
        FRSubdivision(code="FR-27", name="Eure", type_="Metropolitan department"),
        FRSubdivision(code="FR-28", name="Eure-et-Loir", type_="Metropolitan department"),
        FRSubdivision(code="FR-29", name="Finistère", type_="Metropolitan department"),
        FRSubdivision(code="FR-2A", name="Corse-du-Sud", type_="Metropolitan department"),
        FRSubdivision(code="FR-2B", name="Haute-Corse", type_="Metropolitan department"),
        FRSubdivision(code="FR-30", name="Gard", type_="Metropolitan department"),
        FRSubdivision(code="FR-31", name="Haute-Garonne", type_="Metropolitan department"),
        FRSubdivision(code="FR-32", name="Gers", type_="Metropolitan department"),
        FRSubdivision(code="FR-33", name="Gironde", type_="Metropolitan department"),
        FRSubdivision(code="FR-34", name="Hérault", type_="Metropolitan department"),
        FRSubdivision(code="FR-35", name="Ille-et-Vilaine", type_="Metropolitan department"),
        FRSubdivision(code="FR-36", name="Indre", type_="Metropolitan department"),
        FRSubdivision(code="FR-37", name="Indre-et-Loire", type_="Metropolitan department"),
        FRSubdivision(code="FR-38", name="Isère", type_="Metropolitan department"),
        FRSubdivision(code="FR-39", name="Jura", type_="Metropolitan department"),
        FRSubdivision(code="FR-40", name="Landes", type_="Metropolitan department"),
        FRSubdivision(code="FR-41", name="Loir-et-Cher", type_="Metropolitan department"),
        FRSubdivision(code="FR-42", name="Loire", type_="Metropolitan department"),
        FRSubdivision(code="FR-43", name="Haute-Loire", type_="Metropolitan department"),
        FRSubdivision(code="FR-44", name="Loire-Atlantique", type_="Metropolitan department"),
        FRSubdivision(code="FR-45", name="Loiret", type_="Metropolitan department"),
        FRSubdivision(code="FR-46", name="Lot", type_="Metropolitan department"),
        FRSubdivision(code="FR-47", name="Lot-et-Garonne", type_="Metropolitan department"),
        FRSubdivision(code="FR-48", name="Lozère", type_="Metropolitan department"),
        FRSubdivision(code="FR-49", name="Maine-et-Loire", type_="Metropolitan department"),
        FRSubdivision(code="FR-50", name="Manche", type_="Metropolitan department"),
        FRSubdivision(code="FR-51", name="Marne", type_="Metropolitan department"),
        FRSubdivision(code="FR-52", name="Haute-Marne", type_="Metropolitan department"),
        FRSubdivision(code="FR-53", name="Mayenne", type_="Metropolitan department"),
        FRSubdivision(code="FR-54", name="Meurthe-et-Moselle", type_="Metropolitan department"),
        FRSubdivision(code="FR-55", name="Meuse", type_="Metropolitan department"),
        FRSubdivision(code="FR-56", name="Morbihan", type_="Metropolitan department"),
        FRSubdivision(code="FR-57", name="Moselle", type_="Metropolitan department"),
        FRSubdivision(code="FR-58", name="Nièvre", type_="Metropolitan department"),
        FRSubdivision(code="FR-59", name="Nord", type_="Metropolitan department"),
        FRSubdivision(code="FR-60", name="Oise", type_="Metropolitan department"),
        FRSubdivision(code="FR-61", name="Orne", type_="Metropolitan department"),
        FRSubdivision(code="FR-62", name="Pas-de-Calais", type_="Metropolitan department"),
        FRSubdivision(code="FR-63", name="Puy-de-Dôme", type_="Metropolitan department"),
        FRSubdivision(code="FR-64", name="Pyrénées-Atlantiques", type_="Metropolitan department"),
        FRSubdivision(code="FR-65", name="Hautes-Pyrénées", type_="Metropolitan department"),
        FRSubdivision(code="FR-66", name="Pyrénées-Orientales", type_="Metropolitan department"),
        FRSubdivision(code="FR-67", name="Bas-Rhin", type_="Metropolitan department"),
        FRSubdivision(code="FR-68", name="Haut-Rhin", type_="Metropolitan department"),
        FRSubdivision(code="FR-69", name="Rhône", type_="Metropolitan department"),
        FRSubdivision(code="FR-69M", name="Métropole de Lyon", type_="Metropolitan collectivity with special status"),
        FRSubdivision(code="FR-6AE", name="Alsace", type_="European collectivity"),
        FRSubdivision(code="FR-70", name="Haute-Saône", type_="Metropolitan department"),
        FRSubdivision(code="FR-71", name="Saône-et-Loire", type_="Metropolitan department"),
        FRSubdivision(code="FR-72", name="Sarthe", type_="Metropolitan department"),
        FRSubdivision(code="FR-73", name="Savoie", type_="Metropolitan department"),
        FRSubdivision(code="FR-74", name="Haute-Savoie", type_="Metropolitan department"),
        FRSubdivision(code="FR-75C", name="Paris", type_="Metropolitan collectivity with special status"),
        FRSubdivision(code="FR-76", name="Seine-Maritime", type_="Metropolitan department"),
        FRSubdivision(code="FR-77", name="Seine-et-Marne", type_="Metropolitan department"),
        FRSubdivision(code="FR-78", name="Yvelines", type_="Metropolitan department"),
        FRSubdivision(code="FR-79", name="Deux-Sèvres", type_="Metropolitan department"),
        FRSubdivision(code="FR-80", name="Somme", type_="Metropolitan department"),
        FRSubdivision(code="FR-81", name="Tarn", type_="Metropolitan department"),
        FRSubdivision(code="FR-82", name="Tarn-et-Garonne", type_="Metropolitan department"),
        FRSubdivision(code="FR-83", name="Var", type_="Metropolitan department"),
        FRSubdivision(code="FR-84", name="Vaucluse", type_="Metropolitan department"),
        FRSubdivision(code="FR-85", name="Vendée", type_="Metropolitan department"),
        FRSubdivision(code="FR-86", name="Vienne", type_="Metropolitan department"),
        FRSubdivision(code="FR-87", name="Haute-Vienne", type_="Metropolitan department"),
        FRSubdivision(code="FR-88", name="Vosges", type_="Metropolitan department"),
        FRSubdivision(code="FR-89", name="Yonne", type_="Metropolitan department"),
        FRSubdivision(code="FR-90", name="Territoire de Belfort", type_="Metropolitan department"),
        FRSubdivision(code="FR-91", name="Essonne", type_="Metropolitan department"),
        FRSubdivision(code="FR-92", name="Hauts-de-Seine", type_="Metropolitan department"),
        FRSubdivision(code="FR-93", name="Seine-Saint-Denis", type_="Metropolitan department"),
        FRSubdivision(code="FR-94", name="Val-de-Marne", type_="Metropolitan department"),
        FRSubdivision(code="FR-95", name="Val-d'Oise", type_="Metropolitan department"),
        FRSubdivision(code="FR-971", name="Guadeloupe", type_="Overseas departmental collectivity"),
        FRSubdivision(code="FR-972", name="Martinique", type_="Overseas unique territorial collectivity"),
        FRSubdivision(code="FR-973", name="Guyane (française)", type_="Overseas unique territorial collectivity"),
        FRSubdivision(code="FR-974", name="La Réunion", type_="Overseas departmental collectivity"),
        FRSubdivision(code="FR-976", name="Mayotte", type_="Overseas departmental collectivity"),
        FRSubdivision(code="FR-ARA", name="Auvergne-Rhône-Alpes", type_="Metropolitan region"),
        FRSubdivision(code="FR-BFC", name="Bourgogne-Franche-Comté", type_="Metropolitan region"),
        FRSubdivision(code="FR-BL", name="Saint-Barthélemy", type_="Overseas collectivity"),
        FRSubdivision(code="FR-BRE", name="Bretagne", type_="Metropolitan region"),
        FRSubdivision(code="FR-CP", name="Clipperton", type_="Dependency"),
        FRSubdivision(code="FR-CVL", name="Centre-Val de Loire", type_="Metropolitan region"),
        FRSubdivision(code="FR-GES", name="Grand-Est", type_="Metropolitan region"),
        FRSubdivision(code="FR-HDF", name="Hauts-de-France", type_="Metropolitan region"),
        FRSubdivision(code="FR-IDF", name="Île-de-France", type_="Metropolitan region"),
        FRSubdivision(code="FR-MF", name="Saint-Martin", type_="Overseas collectivity"),
        FRSubdivision(code="FR-NAQ", name="Nouvelle-Aquitaine", type_="Metropolitan region"),
        FRSubdivision(code="FR-NC", name="Nouvelle-Calédonie", type_="Overseas collectivity with special status"),
        FRSubdivision(code="FR-NOR", name="Normandie", type_="Metropolitan region"),
        FRSubdivision(code="FR-OCC", name="Occitanie", type_="Metropolitan region"),
        FRSubdivision(code="FR-PAC", name="Provence-Alpes-Côte-d’Azur", type_="Metropolitan region"),
        FRSubdivision(code="FR-PDL", name="Pays-de-la-Loire", type_="Metropolitan region"),
        FRSubdivision(code="FR-PF", name="Polynésie française", type_="Overseas collectivity"),
        FRSubdivision(code="FR-PM", name="Saint-Pierre-et-Miquelon", type_="Overseas collectivity"),
        FRSubdivision(code="FR-TF", name="Terres australes françaises", type_="Overseas territory"),
        FRSubdivision(code="FR-WF", name="Wallis-et-Futuna", type_="Overseas collectivity"),
    ],
)
