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

RUSubdivisionCodeType = Literal[
    "RU-AD",  # Adygeja, Respublika
    "RU-AL",  # Altaj, Respublika
    "RU-ALT",  # Altajskij kraj
    "RU-AMU",  # Amurskaja oblast'
    "RU-ARK",  # Arhangel'skaja oblast'
    "RU-AST",  # Astrahanskaja oblast'
    "RU-BA",  # Bashkortostan, Respublika
    "RU-BEL",  # Belgorodskaja oblast'
    "RU-BRY",  # Brjanskaja oblast'
    "RU-BU",  # Burjatija, Respublika
    "RU-CE",  # Chechenskaya Respublika
    "RU-CHE",  # Chelyabinskaya oblast'
    "RU-CHU",  # Chukotskiy avtonomnyy okrug
    "RU-CU",  # Chuvashskaya Respublika
    "RU-DA",  # Dagestan, Respublika
    "RU-IN",  # Ingushetiya, Respublika
    "RU-IRK",  # Irkutskaja oblast'
    "RU-IVA",  # Ivanovskaja oblast'
    "RU-KAM",  # Kamchatskiy kray
    "RU-KB",  # Kabardino-Balkarskaja Respublika
    "RU-KC",  # Karachayevo-Cherkesskaya Respublika
    "RU-KDA",  # Krasnodarskij kraj
    "RU-KEM",  # Kemerovskaja oblast'
    "RU-KGD",  # Kaliningradskaja oblast'
    "RU-KGN",  # Kurganskaja oblast'
    "RU-KHA",  # Habarovskij kraj
    "RU-KHM",  # Hanty-Mansijskij avtonomnyj okrug
    "RU-KIR",  # Kirovskaja oblast'
    "RU-KK",  # Hakasija, Respublika
    "RU-KL",  # Kalmykija, Respublika
    "RU-KLU",  # Kaluzhskaya oblast'
    "RU-KO",  # Komi, Respublika
    "RU-KOS",  # Kostromskaja oblast'
    "RU-KR",  # Karelija, Respublika
    "RU-KRS",  # Kurskaja oblast'
    "RU-KYA",  # Krasnojarskij kraj
    "RU-LEN",  # Leningradskaja oblast'
    "RU-LIP",  # Lipeckaja oblast'
    "RU-MAG",  # Magadanskaja oblast'
    "RU-ME",  # Marij Èl, Respublika
    "RU-MO",  # Mordovija, Respublika
    "RU-MOS",  # Moskovskaja oblast'
    "RU-MOW",  # Moskva
    "RU-MUR",  # Murmanskaja oblast'
    "RU-NEN",  # Neneckij avtonomnyj okrug
    "RU-NGR",  # Novgorodskaja oblast'
    "RU-NIZ",  # Nizhegorodskaya oblast'
    "RU-NVS",  # Novosibirskaja oblast'
    "RU-OMS",  # Omskaja oblast'
    "RU-ORE",  # Orenburgskaja oblast'
    "RU-ORL",  # Orlovskaja oblast'
    "RU-PER",  # Permskij kraj
    "RU-PNZ",  # Penzenskaja oblast'
    "RU-PRI",  # Primorskij kraj
    "RU-PSK",  # Pskovskaja oblast'
    "RU-ROS",  # Rostovskaja oblast'
    "RU-RYA",  # Rjazanskaja oblast'
    "RU-SA",  # Saha, Respublika
    "RU-SAK",  # Sahalinskaja oblast'
    "RU-SAM",  # Samarskaja oblast'
    "RU-SAR",  # Saratovskaja oblast'
    "RU-SE",  # Severnaja Osetija, Respublika
    "RU-SMO",  # Smolenskaja oblast'
    "RU-SPE",  # Sankt-Peterburg
    "RU-STA",  # Stavropol'skij kraj
    "RU-SVE",  # Sverdlovskaja oblast'
    "RU-TA",  # Tatarstan, Respublika
    "RU-TAM",  # Tambovskaja oblast'
    "RU-TOM",  # Tomskaja oblast'
    "RU-TUL",  # Tul'skaja oblast'
    "RU-TVE",  # Tverskaja oblast'
    "RU-TY",  # Tyva, Respublika
    "RU-TYU",  # Tjumenskaja oblast'
    "RU-UD",  # Udmurtskaja Respublika
    "RU-ULY",  # Ul'janovskaja oblast'
    "RU-VGG",  # Volgogradskaja oblast'
    "RU-VLA",  # Vladimirskaja oblast'
    "RU-VLG",  # Vologodskaja oblast'
    "RU-VOR",  # Voronezhskaya oblast'
    "RU-YAN",  # Jamalo-Neneckij avtonomnyj okrug
    "RU-YAR",  # Jaroslavskaja oblast'
    "RU-YEV",  # Evrejskaja avtonomnaja oblast'
    "RU-ZAB",  # Zabajkal'skij kraj
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class RUSubdivision(Subdivision):
    code: RUSubdivisionCodeType


RU: Final[Country] = Country(
    alpha2="RU",
    alpha3="RUS",
    name="Russian Federation",
    common_name=None,
    official_name=None,
    subdivisions=[
        RUSubdivision(code="RU-AD", name="Adygeja, Respublika", type_="Republic"),
        RUSubdivision(code="RU-AL", name="Altaj, Respublika", type_="Republic"),
        RUSubdivision(code="RU-ALT", name="Altajskij kraj", type_="Administrative territory"),
        RUSubdivision(code="RU-AMU", name="Amurskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-ARK", name="Arhangel'skaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-AST", name="Astrahanskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-BA", name="Bashkortostan, Respublika", type_="Republic"),
        RUSubdivision(code="RU-BEL", name="Belgorodskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-BRY", name="Brjanskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-BU", name="Burjatija, Respublika", type_="Republic"),
        RUSubdivision(code="RU-CE", name="Chechenskaya Respublika", type_="Republic"),
        RUSubdivision(code="RU-CHE", name="Chelyabinskaya oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-CHU", name="Chukotskiy avtonomnyy okrug", type_="Autonomous district"),
        RUSubdivision(code="RU-CU", name="Chuvashskaya Respublika", type_="Republic"),
        RUSubdivision(code="RU-DA", name="Dagestan, Respublika", type_="Republic"),
        RUSubdivision(code="RU-IN", name="Ingushetiya, Respublika", type_="Republic"),
        RUSubdivision(code="RU-IRK", name="Irkutskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-IVA", name="Ivanovskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-KAM", name="Kamchatskiy kray", type_="Administrative territory"),
        RUSubdivision(code="RU-KB", name="Kabardino-Balkarskaja Respublika", type_="Republic"),
        RUSubdivision(code="RU-KC", name="Karachayevo-Cherkesskaya Respublika", type_="Republic"),
        RUSubdivision(code="RU-KDA", name="Krasnodarskij kraj", type_="Administrative territory"),
        RUSubdivision(code="RU-KEM", name="Kemerovskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-KGD", name="Kaliningradskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-KGN", name="Kurganskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-KHA", name="Habarovskij kraj", type_="Administrative territory"),
        RUSubdivision(code="RU-KHM", name="Hanty-Mansijskij avtonomnyj okrug", type_="Autonomous district"),
        RUSubdivision(code="RU-KIR", name="Kirovskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-KK", name="Hakasija, Respublika", type_="Republic"),
        RUSubdivision(code="RU-KL", name="Kalmykija, Respublika", type_="Republic"),
        RUSubdivision(code="RU-KLU", name="Kaluzhskaya oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-KO", name="Komi, Respublika", type_="Republic"),
        RUSubdivision(code="RU-KOS", name="Kostromskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-KR", name="Karelija, Respublika", type_="Republic"),
        RUSubdivision(code="RU-KRS", name="Kurskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-KYA", name="Krasnojarskij kraj", type_="Administrative territory"),
        RUSubdivision(code="RU-LEN", name="Leningradskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-LIP", name="Lipeckaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-MAG", name="Magadanskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-ME", name="Marij Èl, Respublika", type_="Republic"),
        RUSubdivision(code="RU-MO", name="Mordovija, Respublika", type_="Republic"),
        RUSubdivision(code="RU-MOS", name="Moskovskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-MOW", name="Moskva", type_="Autonomous city"),
        RUSubdivision(code="RU-MUR", name="Murmanskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-NEN", name="Neneckij avtonomnyj okrug", type_="Autonomous district"),
        RUSubdivision(code="RU-NGR", name="Novgorodskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-NIZ", name="Nizhegorodskaya oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-NVS", name="Novosibirskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-OMS", name="Omskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-ORE", name="Orenburgskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-ORL", name="Orlovskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-PER", name="Permskij kraj", type_="Administrative territory"),
        RUSubdivision(code="RU-PNZ", name="Penzenskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-PRI", name="Primorskij kraj", type_="Administrative territory"),
        RUSubdivision(code="RU-PSK", name="Pskovskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-ROS", name="Rostovskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-RYA", name="Rjazanskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-SA", name="Saha, Respublika", type_="Republic"),
        RUSubdivision(code="RU-SAK", name="Sahalinskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-SAM", name="Samarskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-SAR", name="Saratovskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-SE", name="Severnaja Osetija, Respublika", type_="Republic"),
        RUSubdivision(code="RU-SMO", name="Smolenskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-SPE", name="Sankt-Peterburg", type_="Autonomous city"),
        RUSubdivision(code="RU-STA", name="Stavropol'skij kraj", type_="Administrative territory"),
        RUSubdivision(code="RU-SVE", name="Sverdlovskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-TA", name="Tatarstan, Respublika", type_="Republic"),
        RUSubdivision(code="RU-TAM", name="Tambovskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-TOM", name="Tomskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-TUL", name="Tul'skaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-TVE", name="Tverskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-TY", name="Tyva, Respublika", type_="Republic"),
        RUSubdivision(code="RU-TYU", name="Tjumenskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-UD", name="Udmurtskaja Respublika", type_="Republic"),
        RUSubdivision(code="RU-ULY", name="Ul'janovskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-VGG", name="Volgogradskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-VLA", name="Vladimirskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-VLG", name="Vologodskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-VOR", name="Voronezhskaya oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-YAN", name="Jamalo-Neneckij avtonomnyj okrug", type_="Autonomous district"),
        RUSubdivision(code="RU-YAR", name="Jaroslavskaja oblast'", type_="Administrative region"),
        RUSubdivision(code="RU-YEV", name="Evrejskaja avtonomnaja oblast'", type_="Autonomous region"),
        RUSubdivision(code="RU-ZAB", name="Zabajkal'skij kraj", type_="Administrative territory"),
    ],
)
