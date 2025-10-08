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

SCSubdivisionCodeType = Literal[
    "SC-01",  # Anse aux Pins
    "SC-02",  # Anse Boileau
    "SC-03",  # Anse Etoile
    "SC-04",  # Au Cap
    "SC-05",  # Anse Royale
    "SC-06",  # Baie Lazare
    "SC-07",  # Baie Sainte Anne
    "SC-08",  # Beau Vallon
    "SC-09",  # Bel Air
    "SC-10",  # Bel Ombre
    "SC-11",  # Cascade
    "SC-12",  # Glacis
    "SC-13",  # Grand Anse Mahe
    "SC-14",  # Grand Anse Praslin
    "SC-15",  # La Digue
    "SC-16",  # English River
    "SC-17",  # Mont Buxton
    "SC-18",  # Mont Fleuri
    "SC-19",  # Plaisance
    "SC-20",  # Pointe Larue
    "SC-21",  # Port Glaud
    "SC-22",  # Saint Louis
    "SC-23",  # Takamaka
    "SC-24",  # Les Mamelles
    "SC-25",  # Roche Caiman
    "SC-26",  # Ile Perseverance I
    "SC-27",  # Ile Perseverance II
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class SCSubdivision(Subdivision):
    code: SCSubdivisionCodeType


SC: Final[Country] = Country(
    alpha2="SC",
    alpha3="SYC",
    name="Seychelles",
    common_name=None,
    official_name="Republic of Seychelles",
    subdivisions=[
        SCSubdivision(code="SC-01", name="Anse aux Pins", type_="District"),
        SCSubdivision(code="SC-02", name="Anse Boileau", type_="District"),
        SCSubdivision(code="SC-03", name="Anse Etoile", type_="District"),
        SCSubdivision(code="SC-04", name="Au Cap", type_="District"),
        SCSubdivision(code="SC-05", name="Anse Royale", type_="District"),
        SCSubdivision(code="SC-06", name="Baie Lazare", type_="District"),
        SCSubdivision(code="SC-07", name="Baie Sainte Anne", type_="District"),
        SCSubdivision(code="SC-08", name="Beau Vallon", type_="District"),
        SCSubdivision(code="SC-09", name="Bel Air", type_="District"),
        SCSubdivision(code="SC-10", name="Bel Ombre", type_="District"),
        SCSubdivision(code="SC-11", name="Cascade", type_="District"),
        SCSubdivision(code="SC-12", name="Glacis", type_="District"),
        SCSubdivision(code="SC-13", name="Grand Anse Mahe", type_="District"),
        SCSubdivision(code="SC-14", name="Grand Anse Praslin", type_="District"),
        SCSubdivision(code="SC-15", name="La Digue", type_="District"),
        SCSubdivision(code="SC-16", name="English River", type_="District"),
        SCSubdivision(code="SC-17", name="Mont Buxton", type_="District"),
        SCSubdivision(code="SC-18", name="Mont Fleuri", type_="District"),
        SCSubdivision(code="SC-19", name="Plaisance", type_="District"),
        SCSubdivision(code="SC-20", name="Pointe Larue", type_="District"),
        SCSubdivision(code="SC-21", name="Port Glaud", type_="District"),
        SCSubdivision(code="SC-22", name="Saint Louis", type_="District"),
        SCSubdivision(code="SC-23", name="Takamaka", type_="District"),
        SCSubdivision(code="SC-24", name="Les Mamelles", type_="District"),
        SCSubdivision(code="SC-25", name="Roche Caiman", type_="District"),
        SCSubdivision(code="SC-26", name="Ile Perseverance I", type_="District"),
        SCSubdivision(code="SC-27", name="Ile Perseverance II", type_="District"),
    ],
)
