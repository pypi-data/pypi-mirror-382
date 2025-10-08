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

ITSubdivisionCodeType = Literal[
    "IT-21",  # Piemonte
    "IT-23",  # Val d'Aoste
    "IT-25",  # Lombardia
    "IT-32",  # Trentino-Alto Adige
    "IT-34",  # Veneto
    "IT-36",  # Friuli Venezia Giulia
    "IT-42",  # Liguria
    "IT-45",  # Emilia-Romagna
    "IT-52",  # Toscana
    "IT-55",  # Umbria
    "IT-57",  # Marche
    "IT-62",  # Lazio
    "IT-65",  # Abruzzo
    "IT-67",  # Molise
    "IT-72",  # Campania
    "IT-75",  # Puglia
    "IT-77",  # Basilicata
    "IT-78",  # Calabria
    "IT-82",  # Sicilia
    "IT-88",  # Sardegna
    "IT-AG",  # Agrigento
    "IT-AL",  # Alessandria
    "IT-AN",  # Ancona
    "IT-AP",  # Ascoli Piceno
    "IT-AQ",  # L'Aquila
    "IT-AR",  # Arezzo
    "IT-AT",  # Asti
    "IT-AV",  # Avellino
    "IT-BA",  # Bari
    "IT-BG",  # Bergamo
    "IT-BI",  # Biella
    "IT-BL",  # Belluno
    "IT-BN",  # Benevento
    "IT-BO",  # Bologna
    "IT-BR",  # Brindisi
    "IT-BS",  # Brescia
    "IT-BT",  # Barletta-Andria-Trani
    "IT-BZ",  # Bolzano
    "IT-CA",  # Cagliari
    "IT-CB",  # Campobasso
    "IT-CE",  # Caserta
    "IT-CH",  # Chieti
    "IT-CL",  # Caltanissetta
    "IT-CN",  # Cuneo
    "IT-CO",  # Como
    "IT-CR",  # Cremona
    "IT-CS",  # Cosenza
    "IT-CT",  # Catania
    "IT-CZ",  # Catanzaro
    "IT-EN",  # Enna
    "IT-FC",  # Forlì-Cesena
    "IT-FE",  # Ferrara
    "IT-FG",  # Foggia
    "IT-FI",  # Firenze
    "IT-FM",  # Fermo
    "IT-FR",  # Frosinone
    "IT-GE",  # Genova
    "IT-GO",  # Gorizia
    "IT-GR",  # Grosseto
    "IT-IM",  # Imperia
    "IT-IS",  # Isernia
    "IT-KR",  # Crotone
    "IT-LC",  # Lecco
    "IT-LE",  # Lecce
    "IT-LI",  # Livorno
    "IT-LO",  # Lodi
    "IT-LT",  # Latina
    "IT-LU",  # Lucca
    "IT-MB",  # Monza e Brianza
    "IT-MC",  # Macerata
    "IT-ME",  # Messina
    "IT-MI",  # Milano
    "IT-MN",  # Mantova
    "IT-MO",  # Modena
    "IT-MS",  # Massa-Carrara
    "IT-MT",  # Matera
    "IT-NA",  # Napoli
    "IT-NO",  # Novara
    "IT-NU",  # Nuoro
    "IT-OR",  # Oristano
    "IT-PA",  # Palermo
    "IT-PC",  # Piacenza
    "IT-PD",  # Padova
    "IT-PE",  # Pescara
    "IT-PG",  # Perugia
    "IT-PI",  # Pisa
    "IT-PN",  # Pordenone
    "IT-PO",  # Prato
    "IT-PR",  # Parma
    "IT-PT",  # Pistoia
    "IT-PU",  # Pesaro e Urbino
    "IT-PV",  # Pavia
    "IT-PZ",  # Potenza
    "IT-RA",  # Ravenna
    "IT-RC",  # Reggio Calabria
    "IT-RE",  # Reggio Emilia
    "IT-RG",  # Ragusa
    "IT-RI",  # Rieti
    "IT-RM",  # Roma
    "IT-RN",  # Rimini
    "IT-RO",  # Rovigo
    "IT-SA",  # Salerno
    "IT-SI",  # Siena
    "IT-SO",  # Sondrio
    "IT-SP",  # La Spezia
    "IT-SR",  # Siracusa
    "IT-SS",  # Sassari
    "IT-SU",  # Sud Sardegna
    "IT-SV",  # Savona
    "IT-TA",  # Taranto
    "IT-TE",  # Teramo
    "IT-TN",  # Trento
    "IT-TO",  # Torino
    "IT-TP",  # Trapani
    "IT-TR",  # Terni
    "IT-TS",  # Trieste
    "IT-TV",  # Treviso
    "IT-UD",  # Udine
    "IT-VA",  # Varese
    "IT-VB",  # Verbano-Cusio-Ossola
    "IT-VC",  # Vercelli
    "IT-VE",  # Venezia
    "IT-VI",  # Vicenza
    "IT-VR",  # Verona
    "IT-VT",  # Viterbo
    "IT-VV",  # Vibo Valentia
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class ITSubdivision(Subdivision):
    code: ITSubdivisionCodeType


IT: Final[Country] = Country(
    alpha2="IT",
    alpha3="ITA",
    name="Italy",
    common_name=None,
    official_name="Italian Republic",
    subdivisions=[
        ITSubdivision(code="IT-21", name="Piemonte", type_="Region"),
        ITSubdivision(code="IT-23", name="Val d'Aoste", type_="Autonomous region"),
        ITSubdivision(code="IT-25", name="Lombardia", type_="Region"),
        ITSubdivision(code="IT-32", name="Trentino-Alto Adige", type_="Autonomous region"),
        ITSubdivision(code="IT-34", name="Veneto", type_="Region"),
        ITSubdivision(code="IT-36", name="Friuli Venezia Giulia", type_="Autonomous region"),
        ITSubdivision(code="IT-42", name="Liguria", type_="Region"),
        ITSubdivision(code="IT-45", name="Emilia-Romagna", type_="Region"),
        ITSubdivision(code="IT-52", name="Toscana", type_="Region"),
        ITSubdivision(code="IT-55", name="Umbria", type_="Region"),
        ITSubdivision(code="IT-57", name="Marche", type_="Region"),
        ITSubdivision(code="IT-62", name="Lazio", type_="Region"),
        ITSubdivision(code="IT-65", name="Abruzzo", type_="Region"),
        ITSubdivision(code="IT-67", name="Molise", type_="Region"),
        ITSubdivision(code="IT-72", name="Campania", type_="Region"),
        ITSubdivision(code="IT-75", name="Puglia", type_="Region"),
        ITSubdivision(code="IT-77", name="Basilicata", type_="Region"),
        ITSubdivision(code="IT-78", name="Calabria", type_="Region"),
        ITSubdivision(code="IT-82", name="Sicilia", type_="Autonomous region"),
        ITSubdivision(code="IT-88", name="Sardegna", type_="Autonomous region"),
        ITSubdivision(code="IT-AG", name="Agrigento", type_="Free municipal consortium"),
        ITSubdivision(code="IT-AL", name="Alessandria", type_="Province"),
        ITSubdivision(code="IT-AN", name="Ancona", type_="Province"),
        ITSubdivision(code="IT-AP", name="Ascoli Piceno", type_="Province"),
        ITSubdivision(code="IT-AQ", name="L'Aquila", type_="Province"),
        ITSubdivision(code="IT-AR", name="Arezzo", type_="Province"),
        ITSubdivision(code="IT-AT", name="Asti", type_="Province"),
        ITSubdivision(code="IT-AV", name="Avellino", type_="Province"),
        ITSubdivision(code="IT-BA", name="Bari", type_="Metropolitan city"),
        ITSubdivision(code="IT-BG", name="Bergamo", type_="Province"),
        ITSubdivision(code="IT-BI", name="Biella", type_="Province"),
        ITSubdivision(code="IT-BL", name="Belluno", type_="Province"),
        ITSubdivision(code="IT-BN", name="Benevento", type_="Province"),
        ITSubdivision(code="IT-BO", name="Bologna", type_="Metropolitan city"),
        ITSubdivision(code="IT-BR", name="Brindisi", type_="Province"),
        ITSubdivision(code="IT-BS", name="Brescia", type_="Province"),
        ITSubdivision(code="IT-BT", name="Barletta-Andria-Trani", type_="Province"),
        ITSubdivision(code="IT-BZ", name="Bolzano", type_="Autonomous province"),
        ITSubdivision(code="IT-CA", name="Cagliari", type_="Metropolitan city"),
        ITSubdivision(code="IT-CB", name="Campobasso", type_="Province"),
        ITSubdivision(code="IT-CE", name="Caserta", type_="Province"),
        ITSubdivision(code="IT-CH", name="Chieti", type_="Province"),
        ITSubdivision(code="IT-CL", name="Caltanissetta", type_="Free municipal consortium"),
        ITSubdivision(code="IT-CN", name="Cuneo", type_="Province"),
        ITSubdivision(code="IT-CO", name="Como", type_="Province"),
        ITSubdivision(code="IT-CR", name="Cremona", type_="Province"),
        ITSubdivision(code="IT-CS", name="Cosenza", type_="Province"),
        ITSubdivision(code="IT-CT", name="Catania", type_="Metropolitan city"),
        ITSubdivision(code="IT-CZ", name="Catanzaro", type_="Province"),
        ITSubdivision(code="IT-EN", name="Enna", type_="Free municipal consortium"),
        ITSubdivision(code="IT-FC", name="Forlì-Cesena", type_="Province"),
        ITSubdivision(code="IT-FE", name="Ferrara", type_="Province"),
        ITSubdivision(code="IT-FG", name="Foggia", type_="Province"),
        ITSubdivision(code="IT-FI", name="Firenze", type_="Metropolitan city"),
        ITSubdivision(code="IT-FM", name="Fermo", type_="Province"),
        ITSubdivision(code="IT-FR", name="Frosinone", type_="Province"),
        ITSubdivision(code="IT-GE", name="Genova", type_="Metropolitan city"),
        ITSubdivision(code="IT-GO", name="Gorizia", type_="Decentralized regional entity"),
        ITSubdivision(code="IT-GR", name="Grosseto", type_="Province"),
        ITSubdivision(code="IT-IM", name="Imperia", type_="Province"),
        ITSubdivision(code="IT-IS", name="Isernia", type_="Province"),
        ITSubdivision(code="IT-KR", name="Crotone", type_="Province"),
        ITSubdivision(code="IT-LC", name="Lecco", type_="Province"),
        ITSubdivision(code="IT-LE", name="Lecce", type_="Province"),
        ITSubdivision(code="IT-LI", name="Livorno", type_="Province"),
        ITSubdivision(code="IT-LO", name="Lodi", type_="Province"),
        ITSubdivision(code="IT-LT", name="Latina", type_="Province"),
        ITSubdivision(code="IT-LU", name="Lucca", type_="Province"),
        ITSubdivision(code="IT-MB", name="Monza e Brianza", type_="Province"),
        ITSubdivision(code="IT-MC", name="Macerata", type_="Province"),
        ITSubdivision(code="IT-ME", name="Messina", type_="Metropolitan city"),
        ITSubdivision(code="IT-MI", name="Milano", type_="Metropolitan city"),
        ITSubdivision(code="IT-MN", name="Mantova", type_="Province"),
        ITSubdivision(code="IT-MO", name="Modena", type_="Province"),
        ITSubdivision(code="IT-MS", name="Massa-Carrara", type_="Province"),
        ITSubdivision(code="IT-MT", name="Matera", type_="Province"),
        ITSubdivision(code="IT-NA", name="Napoli", type_="Metropolitan city"),
        ITSubdivision(code="IT-NO", name="Novara", type_="Province"),
        ITSubdivision(code="IT-NU", name="Nuoro", type_="Province"),
        ITSubdivision(code="IT-OR", name="Oristano", type_="Province"),
        ITSubdivision(code="IT-PA", name="Palermo", type_="Metropolitan city"),
        ITSubdivision(code="IT-PC", name="Piacenza", type_="Province"),
        ITSubdivision(code="IT-PD", name="Padova", type_="Province"),
        ITSubdivision(code="IT-PE", name="Pescara", type_="Province"),
        ITSubdivision(code="IT-PG", name="Perugia", type_="Province"),
        ITSubdivision(code="IT-PI", name="Pisa", type_="Province"),
        ITSubdivision(code="IT-PN", name="Pordenone", type_="Decentralized regional entity"),
        ITSubdivision(code="IT-PO", name="Prato", type_="Province"),
        ITSubdivision(code="IT-PR", name="Parma", type_="Province"),
        ITSubdivision(code="IT-PT", name="Pistoia", type_="Province"),
        ITSubdivision(code="IT-PU", name="Pesaro e Urbino", type_="Province"),
        ITSubdivision(code="IT-PV", name="Pavia", type_="Province"),
        ITSubdivision(code="IT-PZ", name="Potenza", type_="Province"),
        ITSubdivision(code="IT-RA", name="Ravenna", type_="Province"),
        ITSubdivision(code="IT-RC", name="Reggio Calabria", type_="Metropolitan city"),
        ITSubdivision(code="IT-RE", name="Reggio Emilia", type_="Province"),
        ITSubdivision(code="IT-RG", name="Ragusa", type_="Free municipal consortium"),
        ITSubdivision(code="IT-RI", name="Rieti", type_="Province"),
        ITSubdivision(code="IT-RM", name="Roma", type_="Metropolitan city"),
        ITSubdivision(code="IT-RN", name="Rimini", type_="Province"),
        ITSubdivision(code="IT-RO", name="Rovigo", type_="Province"),
        ITSubdivision(code="IT-SA", name="Salerno", type_="Province"),
        ITSubdivision(code="IT-SI", name="Siena", type_="Province"),
        ITSubdivision(code="IT-SO", name="Sondrio", type_="Province"),
        ITSubdivision(code="IT-SP", name="La Spezia", type_="Province"),
        ITSubdivision(code="IT-SR", name="Siracusa", type_="Free municipal consortium"),
        ITSubdivision(code="IT-SS", name="Sassari", type_="Province"),
        ITSubdivision(code="IT-SU", name="Sud Sardegna", type_="Province"),
        ITSubdivision(code="IT-SV", name="Savona", type_="Province"),
        ITSubdivision(code="IT-TA", name="Taranto", type_="Province"),
        ITSubdivision(code="IT-TE", name="Teramo", type_="Province"),
        ITSubdivision(code="IT-TN", name="Trento", type_="Autonomous province"),
        ITSubdivision(code="IT-TO", name="Torino", type_="Metropolitan city"),
        ITSubdivision(code="IT-TP", name="Trapani", type_="Free municipal consortium"),
        ITSubdivision(code="IT-TR", name="Terni", type_="Province"),
        ITSubdivision(code="IT-TS", name="Trieste", type_="Decentralized regional entity"),
        ITSubdivision(code="IT-TV", name="Treviso", type_="Province"),
        ITSubdivision(code="IT-UD", name="Udine", type_="Decentralized regional entity"),
        ITSubdivision(code="IT-VA", name="Varese", type_="Province"),
        ITSubdivision(code="IT-VB", name="Verbano-Cusio-Ossola", type_="Province"),
        ITSubdivision(code="IT-VC", name="Vercelli", type_="Province"),
        ITSubdivision(code="IT-VE", name="Venezia", type_="Metropolitan city"),
        ITSubdivision(code="IT-VI", name="Vicenza", type_="Province"),
        ITSubdivision(code="IT-VR", name="Verona", type_="Province"),
        ITSubdivision(code="IT-VT", name="Viterbo", type_="Province"),
        ITSubdivision(code="IT-VV", name="Vibo Valentia", type_="Province"),
    ],
)
