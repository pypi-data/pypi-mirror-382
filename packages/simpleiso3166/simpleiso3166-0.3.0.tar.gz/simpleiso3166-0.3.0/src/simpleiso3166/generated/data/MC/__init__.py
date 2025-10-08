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

MCSubdivisionCodeType = Literal[
    "MC-CL",  # La Colle
    "MC-CO",  # La Condamine
    "MC-FO",  # Fontvieille
    "MC-GA",  # La Gare
    "MC-JE",  # Jardin Exotique
    "MC-LA",  # Larvotto
    "MC-MA",  # Malbousquet
    "MC-MC",  # Monte-Carlo
    "MC-MG",  # Moneghetti
    "MC-MO",  # Monaco-Ville
    "MC-MU",  # Moulins
    "MC-PH",  # Port-Hercule
    "MC-SD",  # Sainte-Dévote
    "MC-SO",  # La Source
    "MC-SP",  # Spélugues
    "MC-SR",  # Saint-Roman
    "MC-VR",  # Vallon de la Rousse
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class MCSubdivision(Subdivision):
    code: MCSubdivisionCodeType


MC: Final[Country] = Country(
    alpha2="MC",
    alpha3="MCO",
    name="Monaco",
    common_name=None,
    official_name="Principality of Monaco",
    subdivisions=[
        MCSubdivision(code="MC-CL", name="La Colle", type_="Quarter"),
        MCSubdivision(code="MC-CO", name="La Condamine", type_="Quarter"),
        MCSubdivision(code="MC-FO", name="Fontvieille", type_="Quarter"),
        MCSubdivision(code="MC-GA", name="La Gare", type_="Quarter"),
        MCSubdivision(code="MC-JE", name="Jardin Exotique", type_="Quarter"),
        MCSubdivision(code="MC-LA", name="Larvotto", type_="Quarter"),
        MCSubdivision(code="MC-MA", name="Malbousquet", type_="Quarter"),
        MCSubdivision(code="MC-MC", name="Monte-Carlo", type_="Quarter"),
        MCSubdivision(code="MC-MG", name="Moneghetti", type_="Quarter"),
        MCSubdivision(code="MC-MO", name="Monaco-Ville", type_="Quarter"),
        MCSubdivision(code="MC-MU", name="Moulins", type_="Quarter"),
        MCSubdivision(code="MC-PH", name="Port-Hercule", type_="Quarter"),
        MCSubdivision(code="MC-SD", name="Sainte-Dévote", type_="Quarter"),
        MCSubdivision(code="MC-SO", name="La Source", type_="Quarter"),
        MCSubdivision(code="MC-SP", name="Spélugues", type_="Quarter"),
        MCSubdivision(code="MC-SR", name="Saint-Roman", type_="Quarter"),
        MCSubdivision(code="MC-VR", name="Vallon de la Rousse", type_="Quarter"),
    ],
)
