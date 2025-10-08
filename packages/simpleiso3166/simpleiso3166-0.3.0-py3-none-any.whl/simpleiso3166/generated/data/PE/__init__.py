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

PESubdivisionCodeType = Literal[
    "PE-AMA",  # Amarumayu
    "PE-ANC",  # Ancash
    "PE-APU",  # Apurimaq
    "PE-ARE",  # Arequipa
    "PE-AYA",  # Ayacucho
    "PE-CAJ",  # Cajamarca
    "PE-CAL",  # El Callao
    "PE-CUS",  # Cusco
    "PE-HUC",  # Huánuco
    "PE-HUV",  # Huancavelica
    "PE-ICA",  # Ica
    "PE-JUN",  # Hunin
    "PE-LAL",  # La Libertad
    "PE-LAM",  # Lambayeque
    "PE-LIM",  # Lima
    "PE-LMA",  # Lima hatun llaqta
    "PE-LOR",  # Loreto
    "PE-MDD",  # Madre de Dios
    "PE-MOQ",  # Moquegua
    "PE-PAS",  # Pasco
    "PE-PIU",  # Piura
    "PE-PUN",  # Puno
    "PE-SAM",  # San Martin
    "PE-TAC",  # Tacna
    "PE-TUM",  # Tumbes
    "PE-UCA",  # Ucayali
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class PESubdivision(Subdivision):
    code: PESubdivisionCodeType


PE: Final[Country] = Country(
    alpha2="PE",
    alpha3="PER",
    name="Peru",
    common_name=None,
    official_name="Republic of Peru",
    subdivisions=[
        PESubdivision(code="PE-AMA", name="Amarumayu", type_="Region"),
        PESubdivision(code="PE-ANC", name="Ancash", type_="Region"),
        PESubdivision(code="PE-APU", name="Apurimaq", type_="Region"),
        PESubdivision(code="PE-ARE", name="Arequipa", type_="Region"),
        PESubdivision(code="PE-AYA", name="Ayacucho", type_="Region"),
        PESubdivision(code="PE-CAJ", name="Cajamarca", type_="Region"),
        PESubdivision(code="PE-CAL", name="El Callao", type_="Region"),
        PESubdivision(code="PE-CUS", name="Cusco", type_="Region"),
        PESubdivision(code="PE-HUC", name="Huánuco", type_="Region"),
        PESubdivision(code="PE-HUV", name="Huancavelica", type_="Region"),
        PESubdivision(code="PE-ICA", name="Ica", type_="Region"),
        PESubdivision(code="PE-JUN", name="Hunin", type_="Region"),
        PESubdivision(code="PE-LAL", name="La Libertad", type_="Region"),
        PESubdivision(code="PE-LAM", name="Lambayeque", type_="Region"),
        PESubdivision(code="PE-LIM", name="Lima", type_="Region"),
        PESubdivision(code="PE-LMA", name="Lima hatun llaqta", type_="Municipality"),
        PESubdivision(code="PE-LOR", name="Loreto", type_="Region"),
        PESubdivision(code="PE-MDD", name="Madre de Dios", type_="Region"),
        PESubdivision(code="PE-MOQ", name="Moquegua", type_="Region"),
        PESubdivision(code="PE-PAS", name="Pasco", type_="Region"),
        PESubdivision(code="PE-PIU", name="Piura", type_="Region"),
        PESubdivision(code="PE-PUN", name="Puno", type_="Region"),
        PESubdivision(code="PE-SAM", name="San Martin", type_="Region"),
        PESubdivision(code="PE-TAC", name="Tacna", type_="Region"),
        PESubdivision(code="PE-TUM", name="Tumbes", type_="Region"),
        PESubdivision(code="PE-UCA", name="Ucayali", type_="Region"),
    ],
)
