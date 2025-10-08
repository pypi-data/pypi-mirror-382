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

PTSubdivisionCodeType = Literal[
    "PT-01",  # Aveiro
    "PT-02",  # Beja
    "PT-03",  # Braga
    "PT-04",  # Bragança
    "PT-05",  # Castelo Branco
    "PT-06",  # Coimbra
    "PT-07",  # Évora
    "PT-08",  # Faro
    "PT-09",  # Guarda
    "PT-10",  # Leiria
    "PT-11",  # Lisboa
    "PT-12",  # Portalegre
    "PT-13",  # Porto
    "PT-14",  # Santarém
    "PT-15",  # Setúbal
    "PT-16",  # Viana do Castelo
    "PT-17",  # Vila Real
    "PT-18",  # Viseu
    "PT-20",  # Região Autónoma dos Açores
    "PT-30",  # Região Autónoma da Madeira
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class PTSubdivision(Subdivision):
    code: PTSubdivisionCodeType


PT: Final[Country] = Country(
    alpha2="PT",
    alpha3="PRT",
    name="Portugal",
    common_name=None,
    official_name="Portuguese Republic",
    subdivisions=[
        PTSubdivision(code="PT-01", name="Aveiro", type_="District"),
        PTSubdivision(code="PT-02", name="Beja", type_="District"),
        PTSubdivision(code="PT-03", name="Braga", type_="District"),
        PTSubdivision(code="PT-04", name="Bragança", type_="District"),
        PTSubdivision(code="PT-05", name="Castelo Branco", type_="District"),
        PTSubdivision(code="PT-06", name="Coimbra", type_="District"),
        PTSubdivision(code="PT-07", name="Évora", type_="District"),
        PTSubdivision(code="PT-08", name="Faro", type_="District"),
        PTSubdivision(code="PT-09", name="Guarda", type_="District"),
        PTSubdivision(code="PT-10", name="Leiria", type_="District"),
        PTSubdivision(code="PT-11", name="Lisboa", type_="District"),
        PTSubdivision(code="PT-12", name="Portalegre", type_="District"),
        PTSubdivision(code="PT-13", name="Porto", type_="District"),
        PTSubdivision(code="PT-14", name="Santarém", type_="District"),
        PTSubdivision(code="PT-15", name="Setúbal", type_="District"),
        PTSubdivision(code="PT-16", name="Viana do Castelo", type_="District"),
        PTSubdivision(code="PT-17", name="Vila Real", type_="District"),
        PTSubdivision(code="PT-18", name="Viseu", type_="District"),
        PTSubdivision(code="PT-20", name="Região Autónoma dos Açores", type_="Autonomous region"),
        PTSubdivision(code="PT-30", name="Região Autónoma da Madeira", type_="Autonomous region"),
    ],
)
