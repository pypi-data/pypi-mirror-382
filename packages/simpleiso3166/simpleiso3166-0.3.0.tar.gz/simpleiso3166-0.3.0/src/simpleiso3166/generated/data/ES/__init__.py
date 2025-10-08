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

ESSubdivisionCodeType = Literal[
    "ES-A",  # Alacant*
    "ES-AB",  # Albacete
    "ES-AL",  # Almería
    "ES-AN",  # Andalucía
    "ES-AR",  # Aragón
    "ES-AS",  # Asturias, Principado de
    "ES-AV",  # Ávila
    "ES-B",  # Barcelona [Barcelona]
    "ES-BA",  # Badajoz
    "ES-BI",  # Bizkaia
    "ES-BU",  # Burgos
    "ES-C",  # A Coruña [La Coruña]
    "ES-CA",  # Cádiz
    "ES-CB",  # Cantabria
    "ES-CC",  # Cáceres
    "ES-CE",  # Ceuta
    "ES-CL",  # Castilla y León
    "ES-CM",  # Castilla-La Mancha
    "ES-CN",  # Canarias
    "ES-CO",  # Córdoba
    "ES-CR",  # Ciudad Real
    "ES-CS",  # Castelló*
    "ES-CT",  # Catalunya [Cataluña]
    "ES-CU",  # Cuenca
    "ES-EX",  # Extremadura
    "ES-GA",  # Galicia [Galicia]
    "ES-GC",  # Las Palmas
    "ES-GI",  # Girona [Gerona]
    "ES-GR",  # Granada
    "ES-GU",  # Guadalajara
    "ES-H",  # Huelva
    "ES-HU",  # Huesca
    "ES-IB",  # Illes Balears [Islas Baleares]
    "ES-J",  # Jaén
    "ES-L",  # Lleida [Lérida]
    "ES-LE",  # León
    "ES-LO",  # La Rioja
    "ES-LU",  # Lugo [Lugo]
    "ES-M",  # Madrid
    "ES-MA",  # Málaga
    "ES-MC",  # Murcia, Región de
    "ES-MD",  # Madrid, Comunidad de
    "ES-ML",  # Melilla
    "ES-MU",  # Murcia
    "ES-NA",  # Nafarroa*
    "ES-NC",  # Nafarroako Foru Komunitatea*
    "ES-O",  # Asturias
    "ES-OR",  # Ourense [Orense]
    "ES-P",  # Palencia
    "ES-PM",  # Illes Balears [Islas Baleares]
    "ES-PO",  # Pontevedra [Pontevedra]
    "ES-PV",  # Euskal Herria
    "ES-RI",  # La Rioja
    "ES-S",  # Cantabria
    "ES-SA",  # Salamanca
    "ES-SE",  # Sevilla
    "ES-SG",  # Segovia
    "ES-SO",  # Soria
    "ES-SS",  # Gipuzkoa
    "ES-T",  # Tarragona [Tarragona]
    "ES-TE",  # Teruel
    "ES-TF",  # Santa Cruz de Tenerife
    "ES-TO",  # Toledo
    "ES-V",  # Valencia
    "ES-VA",  # Valladolid
    "ES-VC",  # Valenciana, Comunidad
    "ES-VI",  # Araba*
    "ES-Z",  # Zaragoza
    "ES-ZA",  # Zamora
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class ESSubdivision(Subdivision):
    code: ESSubdivisionCodeType


ES: Final[Country] = Country(
    alpha2="ES",
    alpha3="ESP",
    name="Spain",
    common_name=None,
    official_name="Kingdom of Spain",
    subdivisions=[
        ESSubdivision(code="ES-A", name="Alacant*", type_="Province"),
        ESSubdivision(code="ES-AB", name="Albacete", type_="Province"),
        ESSubdivision(code="ES-AL", name="Almería", type_="Province"),
        ESSubdivision(code="ES-AN", name="Andalucía", type_="Autonomous community"),
        ESSubdivision(code="ES-AR", name="Aragón", type_="Autonomous community"),
        ESSubdivision(code="ES-AS", name="Asturias, Principado de", type_="Autonomous community"),
        ESSubdivision(code="ES-AV", name="Ávila", type_="Province"),
        ESSubdivision(code="ES-B", name="Barcelona [Barcelona]", type_="Province"),
        ESSubdivision(code="ES-BA", name="Badajoz", type_="Province"),
        ESSubdivision(code="ES-BI", name="Bizkaia", type_="Province"),
        ESSubdivision(code="ES-BU", name="Burgos", type_="Province"),
        ESSubdivision(code="ES-C", name="A Coruña [La Coruña]", type_="Province"),
        ESSubdivision(code="ES-CA", name="Cádiz", type_="Province"),
        ESSubdivision(code="ES-CB", name="Cantabria", type_="Autonomous community"),
        ESSubdivision(code="ES-CC", name="Cáceres", type_="Province"),
        ESSubdivision(code="ES-CE", name="Ceuta", type_="Autonomous city in north africa"),
        ESSubdivision(code="ES-CL", name="Castilla y León", type_="Autonomous community"),
        ESSubdivision(code="ES-CM", name="Castilla-La Mancha", type_="Autonomous community"),
        ESSubdivision(code="ES-CN", name="Canarias", type_="Autonomous community"),
        ESSubdivision(code="ES-CO", name="Córdoba", type_="Province"),
        ESSubdivision(code="ES-CR", name="Ciudad Real", type_="Province"),
        ESSubdivision(code="ES-CS", name="Castelló*", type_="Province"),
        ESSubdivision(code="ES-CT", name="Catalunya [Cataluña]", type_="Autonomous community"),
        ESSubdivision(code="ES-CU", name="Cuenca", type_="Province"),
        ESSubdivision(code="ES-EX", name="Extremadura", type_="Autonomous community"),
        ESSubdivision(code="ES-GA", name="Galicia [Galicia]", type_="Autonomous community"),
        ESSubdivision(code="ES-GC", name="Las Palmas", type_="Province"),
        ESSubdivision(code="ES-GI", name="Girona [Gerona]", type_="Province"),
        ESSubdivision(code="ES-GR", name="Granada", type_="Province"),
        ESSubdivision(code="ES-GU", name="Guadalajara", type_="Province"),
        ESSubdivision(code="ES-H", name="Huelva", type_="Province"),
        ESSubdivision(code="ES-HU", name="Huesca", type_="Province"),
        ESSubdivision(code="ES-IB", name="Illes Balears [Islas Baleares]", type_="Autonomous community"),
        ESSubdivision(code="ES-J", name="Jaén", type_="Province"),
        ESSubdivision(code="ES-L", name="Lleida [Lérida]", type_="Province"),
        ESSubdivision(code="ES-LE", name="León", type_="Province"),
        ESSubdivision(code="ES-LO", name="La Rioja", type_="Province"),
        ESSubdivision(code="ES-LU", name="Lugo [Lugo]", type_="Province"),
        ESSubdivision(code="ES-M", name="Madrid", type_="Province"),
        ESSubdivision(code="ES-MA", name="Málaga", type_="Province"),
        ESSubdivision(code="ES-MC", name="Murcia, Región de", type_="Autonomous community"),
        ESSubdivision(code="ES-MD", name="Madrid, Comunidad de", type_="Autonomous community"),
        ESSubdivision(code="ES-ML", name="Melilla", type_="Autonomous city in north africa"),
        ESSubdivision(code="ES-MU", name="Murcia", type_="Province"),
        ESSubdivision(code="ES-NA", name="Nafarroa*", type_="Province"),
        ESSubdivision(code="ES-NC", name="Nafarroako Foru Komunitatea*", type_="Autonomous community"),
        ESSubdivision(code="ES-O", name="Asturias", type_="Province"),
        ESSubdivision(code="ES-OR", name="Ourense [Orense]", type_="Province"),
        ESSubdivision(code="ES-P", name="Palencia", type_="Province"),
        ESSubdivision(code="ES-PM", name="Illes Balears [Islas Baleares]", type_="Province"),
        ESSubdivision(code="ES-PO", name="Pontevedra [Pontevedra]", type_="Province"),
        ESSubdivision(code="ES-PV", name="Euskal Herria", type_="Autonomous community"),
        ESSubdivision(code="ES-RI", name="La Rioja", type_="Autonomous community"),
        ESSubdivision(code="ES-S", name="Cantabria", type_="Province"),
        ESSubdivision(code="ES-SA", name="Salamanca", type_="Province"),
        ESSubdivision(code="ES-SE", name="Sevilla", type_="Province"),
        ESSubdivision(code="ES-SG", name="Segovia", type_="Province"),
        ESSubdivision(code="ES-SO", name="Soria", type_="Province"),
        ESSubdivision(code="ES-SS", name="Gipuzkoa", type_="Province"),
        ESSubdivision(code="ES-T", name="Tarragona [Tarragona]", type_="Province"),
        ESSubdivision(code="ES-TE", name="Teruel", type_="Province"),
        ESSubdivision(code="ES-TF", name="Santa Cruz de Tenerife", type_="Province"),
        ESSubdivision(code="ES-TO", name="Toledo", type_="Province"),
        ESSubdivision(code="ES-V", name="Valencia", type_="Province"),
        ESSubdivision(code="ES-VA", name="Valladolid", type_="Province"),
        ESSubdivision(code="ES-VC", name="Valenciana, Comunidad", type_="Autonomous community"),
        ESSubdivision(code="ES-VI", name="Araba*", type_="Province"),
        ESSubdivision(code="ES-Z", name="Zaragoza", type_="Province"),
        ESSubdivision(code="ES-ZA", name="Zamora", type_="Province"),
    ],
)
