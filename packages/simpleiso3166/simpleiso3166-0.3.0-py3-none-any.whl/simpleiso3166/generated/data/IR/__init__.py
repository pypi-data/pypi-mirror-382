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

IRSubdivisionCodeType = Literal[
    "IR-00",  # Markazī
    "IR-01",  # Gīlān
    "IR-02",  # Māzandarān
    "IR-03",  # Āz̄ārbāyjān-e Shārqī
    "IR-04",  # Āz̄ārbāyjān-e Ghārbī
    "IR-05",  # Kermānshāh
    "IR-06",  # Khūzestān
    "IR-07",  # Fārs
    "IR-08",  # Kermān
    "IR-09",  # Khorāsān-e Raẕavī
    "IR-10",  # Eşfahān
    "IR-11",  # Sīstān va Balūchestān
    "IR-12",  # Kordestān
    "IR-13",  # Hamadān
    "IR-14",  # Chahār Maḩāl va Bakhtīārī
    "IR-15",  # Lorestān
    "IR-16",  # Īlām
    "IR-17",  # Kohgīlūyeh va Bowyer Aḩmad
    "IR-18",  # Būshehr
    "IR-19",  # Zanjān
    "IR-20",  # Semnān
    "IR-21",  # Yazd
    "IR-22",  # Hormozgān
    "IR-23",  # Tehrān
    "IR-24",  # Ardabīl
    "IR-25",  # Qom
    "IR-26",  # Qazvīn
    "IR-27",  # Golestān
    "IR-28",  # Khorāsān-e Shomālī
    "IR-29",  # Khorāsān-e Jonūbī
    "IR-30",  # Alborz
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class IRSubdivision(Subdivision):
    code: IRSubdivisionCodeType


IR: Final[Country] = Country(
    alpha2="IR",
    alpha3="IRN",
    name="Iran, Islamic Republic of",
    common_name="Iran",
    official_name="Islamic Republic of Iran",
    subdivisions=[
        IRSubdivision(code="IR-00", name="Markazī", type_="Province"),
        IRSubdivision(code="IR-01", name="Gīlān", type_="Province"),
        IRSubdivision(code="IR-02", name="Māzandarān", type_="Province"),
        IRSubdivision(code="IR-03", name="Āz̄ārbāyjān-e Shārqī", type_="Province"),
        IRSubdivision(code="IR-04", name="Āz̄ārbāyjān-e Ghārbī", type_="Province"),
        IRSubdivision(code="IR-05", name="Kermānshāh", type_="Province"),
        IRSubdivision(code="IR-06", name="Khūzestān", type_="Province"),
        IRSubdivision(code="IR-07", name="Fārs", type_="Province"),
        IRSubdivision(code="IR-08", name="Kermān", type_="Province"),
        IRSubdivision(code="IR-09", name="Khorāsān-e Raẕavī", type_="Province"),
        IRSubdivision(code="IR-10", name="Eşfahān", type_="Province"),
        IRSubdivision(code="IR-11", name="Sīstān va Balūchestān", type_="Province"),
        IRSubdivision(code="IR-12", name="Kordestān", type_="Province"),
        IRSubdivision(code="IR-13", name="Hamadān", type_="Province"),
        IRSubdivision(code="IR-14", name="Chahār Maḩāl va Bakhtīārī", type_="Province"),
        IRSubdivision(code="IR-15", name="Lorestān", type_="Province"),
        IRSubdivision(code="IR-16", name="Īlām", type_="Province"),
        IRSubdivision(code="IR-17", name="Kohgīlūyeh va Bowyer Aḩmad", type_="Province"),
        IRSubdivision(code="IR-18", name="Būshehr", type_="Province"),
        IRSubdivision(code="IR-19", name="Zanjān", type_="Province"),
        IRSubdivision(code="IR-20", name="Semnān", type_="Province"),
        IRSubdivision(code="IR-21", name="Yazd", type_="Province"),
        IRSubdivision(code="IR-22", name="Hormozgān", type_="Province"),
        IRSubdivision(code="IR-23", name="Tehrān", type_="Province"),
        IRSubdivision(code="IR-24", name="Ardabīl", type_="Province"),
        IRSubdivision(code="IR-25", name="Qom", type_="Province"),
        IRSubdivision(code="IR-26", name="Qazvīn", type_="Province"),
        IRSubdivision(code="IR-27", name="Golestān", type_="Province"),
        IRSubdivision(code="IR-28", name="Khorāsān-e Shomālī", type_="Province"),
        IRSubdivision(code="IR-29", name="Khorāsān-e Jonūbī", type_="Province"),
        IRSubdivision(code="IR-30", name="Alborz", type_="Province"),
    ],
)
