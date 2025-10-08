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

AZSubdivisionCodeType = Literal[
    "AZ-ABS",  # Abşeron
    "AZ-AGA",  # Ağstafa
    "AZ-AGC",  # Ağcabədi
    "AZ-AGM",  # Ağdam
    "AZ-AGS",  # Ağdaş
    "AZ-AGU",  # Ağsu
    "AZ-AST",  # Astara
    "AZ-BA",  # Bakı
    "AZ-BAB",  # Babək
    "AZ-BAL",  # Balakən
    "AZ-BAR",  # Bərdə
    "AZ-BEY",  # Beyləqan
    "AZ-BIL",  # Biləsuvar
    "AZ-CAB",  # Cəbrayıl
    "AZ-CAL",  # Cəlilabad
    "AZ-CUL",  # Culfa
    "AZ-DAS",  # Daşkəsən
    "AZ-FUZ",  # Füzuli
    "AZ-GA",  # Gəncə
    "AZ-GAD",  # Gədəbəy
    "AZ-GOR",  # Goranboy
    "AZ-GOY",  # Göyçay
    "AZ-GYG",  # Göygöl
    "AZ-HAC",  # Hacıqabul
    "AZ-IMI",  # İmişli
    "AZ-ISM",  # İsmayıllı
    "AZ-KAL",  # Kəlbəcər
    "AZ-KAN",  # Kǝngǝrli
    "AZ-KUR",  # Kürdəmir
    "AZ-LA",  # Lənkəran
    "AZ-LAC",  # Laçın
    "AZ-LAN",  # Lənkəran
    "AZ-LER",  # Lerik
    "AZ-MAS",  # Masallı
    "AZ-MI",  # Mingəçevir
    "AZ-NA",  # Naftalan
    "AZ-NEF",  # Neftçala
    "AZ-NV",  # Naxçıvan
    "AZ-NX",  # Naxçıvan
    "AZ-OGU",  # Oğuz
    "AZ-ORD",  # Ordubad
    "AZ-QAB",  # Qəbələ
    "AZ-QAX",  # Qax
    "AZ-QAZ",  # Qazax
    "AZ-QBA",  # Quba
    "AZ-QBI",  # Qubadlı
    "AZ-QOB",  # Qobustan
    "AZ-QUS",  # Qusar
    "AZ-SA",  # Şəki
    "AZ-SAB",  # Sabirabad
    "AZ-SAD",  # Sədərək
    "AZ-SAH",  # Şahbuz
    "AZ-SAK",  # Şəki
    "AZ-SAL",  # Salyan
    "AZ-SAR",  # Şərur
    "AZ-SAT",  # Saatlı
    "AZ-SBN",  # Şabran
    "AZ-SIY",  # Siyəzən
    "AZ-SKR",  # Şəmkir
    "AZ-SM",  # Sumqayıt
    "AZ-SMI",  # Şamaxı
    "AZ-SMX",  # Samux
    "AZ-SR",  # Şirvan
    "AZ-SUS",  # Şuşa
    "AZ-TAR",  # Tərtər
    "AZ-TOV",  # Tovuz
    "AZ-UCA",  # Ucar
    "AZ-XA",  # Xankəndi
    "AZ-XAC",  # Xaçmaz
    "AZ-XCI",  # Xocalı
    "AZ-XIZ",  # Xızı
    "AZ-XVD",  # Xocavənd
    "AZ-YAR",  # Yardımlı
    "AZ-YE",  # Yevlax
    "AZ-YEV",  # Yevlax
    "AZ-ZAN",  # Zəngilan
    "AZ-ZAQ",  # Zaqatala
    "AZ-ZAR",  # Zərdab
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class AZSubdivision(Subdivision):
    code: AZSubdivisionCodeType


AZ: Final[Country] = Country(
    alpha2="AZ",
    alpha3="AZE",
    name="Azerbaijan",
    common_name=None,
    official_name="Republic of Azerbaijan",
    subdivisions=[
        AZSubdivision(code="AZ-ABS", name="Abşeron", type_="Rayon"),
        AZSubdivision(code="AZ-AGA", name="Ağstafa", type_="Rayon"),
        AZSubdivision(code="AZ-AGC", name="Ağcabədi", type_="Rayon"),
        AZSubdivision(code="AZ-AGM", name="Ağdam", type_="Rayon"),
        AZSubdivision(code="AZ-AGS", name="Ağdaş", type_="Rayon"),
        AZSubdivision(code="AZ-AGU", name="Ağsu", type_="Rayon"),
        AZSubdivision(code="AZ-AST", name="Astara", type_="Rayon"),
        AZSubdivision(code="AZ-BA", name="Bakı", type_="Municipality"),
        AZSubdivision(code="AZ-BAB", name="Babək", type_="Rayon"),
        AZSubdivision(code="AZ-BAL", name="Balakən", type_="Rayon"),
        AZSubdivision(code="AZ-BAR", name="Bərdə", type_="Rayon"),
        AZSubdivision(code="AZ-BEY", name="Beyləqan", type_="Rayon"),
        AZSubdivision(code="AZ-BIL", name="Biləsuvar", type_="Rayon"),
        AZSubdivision(code="AZ-CAB", name="Cəbrayıl", type_="Rayon"),
        AZSubdivision(code="AZ-CAL", name="Cəlilabad", type_="Rayon"),
        AZSubdivision(code="AZ-CUL", name="Culfa", type_="Rayon"),
        AZSubdivision(code="AZ-DAS", name="Daşkəsən", type_="Rayon"),
        AZSubdivision(code="AZ-FUZ", name="Füzuli", type_="Rayon"),
        AZSubdivision(code="AZ-GA", name="Gəncə", type_="Municipality"),
        AZSubdivision(code="AZ-GAD", name="Gədəbəy", type_="Rayon"),
        AZSubdivision(code="AZ-GOR", name="Goranboy", type_="Rayon"),
        AZSubdivision(code="AZ-GOY", name="Göyçay", type_="Rayon"),
        AZSubdivision(code="AZ-GYG", name="Göygöl", type_="Rayon"),
        AZSubdivision(code="AZ-HAC", name="Hacıqabul", type_="Rayon"),
        AZSubdivision(code="AZ-IMI", name="İmişli", type_="Rayon"),
        AZSubdivision(code="AZ-ISM", name="İsmayıllı", type_="Rayon"),
        AZSubdivision(code="AZ-KAL", name="Kəlbəcər", type_="Rayon"),
        AZSubdivision(code="AZ-KAN", name="Kǝngǝrli", type_="Rayon"),
        AZSubdivision(code="AZ-KUR", name="Kürdəmir", type_="Rayon"),
        AZSubdivision(code="AZ-LA", name="Lənkəran", type_="Municipality"),
        AZSubdivision(code="AZ-LAC", name="Laçın", type_="Rayon"),
        AZSubdivision(code="AZ-LAN", name="Lənkəran", type_="Rayon"),
        AZSubdivision(code="AZ-LER", name="Lerik", type_="Rayon"),
        AZSubdivision(code="AZ-MAS", name="Masallı", type_="Rayon"),
        AZSubdivision(code="AZ-MI", name="Mingəçevir", type_="Municipality"),
        AZSubdivision(code="AZ-NA", name="Naftalan", type_="Municipality"),
        AZSubdivision(code="AZ-NEF", name="Neftçala", type_="Rayon"),
        AZSubdivision(code="AZ-NV", name="Naxçıvan", type_="Municipality"),
        AZSubdivision(code="AZ-NX", name="Naxçıvan", type_="Autonomous republic"),
        AZSubdivision(code="AZ-OGU", name="Oğuz", type_="Rayon"),
        AZSubdivision(code="AZ-ORD", name="Ordubad", type_="Rayon"),
        AZSubdivision(code="AZ-QAB", name="Qəbələ", type_="Rayon"),
        AZSubdivision(code="AZ-QAX", name="Qax", type_="Rayon"),
        AZSubdivision(code="AZ-QAZ", name="Qazax", type_="Rayon"),
        AZSubdivision(code="AZ-QBA", name="Quba", type_="Rayon"),
        AZSubdivision(code="AZ-QBI", name="Qubadlı", type_="Rayon"),
        AZSubdivision(code="AZ-QOB", name="Qobustan", type_="Rayon"),
        AZSubdivision(code="AZ-QUS", name="Qusar", type_="Rayon"),
        AZSubdivision(code="AZ-SA", name="Şəki", type_="Municipality"),
        AZSubdivision(code="AZ-SAB", name="Sabirabad", type_="Rayon"),
        AZSubdivision(code="AZ-SAD", name="Sədərək", type_="Rayon"),
        AZSubdivision(code="AZ-SAH", name="Şahbuz", type_="Rayon"),
        AZSubdivision(code="AZ-SAK", name="Şəki", type_="Rayon"),
        AZSubdivision(code="AZ-SAL", name="Salyan", type_="Rayon"),
        AZSubdivision(code="AZ-SAR", name="Şərur", type_="Rayon"),
        AZSubdivision(code="AZ-SAT", name="Saatlı", type_="Rayon"),
        AZSubdivision(code="AZ-SBN", name="Şabran", type_="Rayon"),
        AZSubdivision(code="AZ-SIY", name="Siyəzən", type_="Rayon"),
        AZSubdivision(code="AZ-SKR", name="Şəmkir", type_="Rayon"),
        AZSubdivision(code="AZ-SM", name="Sumqayıt", type_="Municipality"),
        AZSubdivision(code="AZ-SMI", name="Şamaxı", type_="Rayon"),
        AZSubdivision(code="AZ-SMX", name="Samux", type_="Rayon"),
        AZSubdivision(code="AZ-SR", name="Şirvan", type_="Municipality"),
        AZSubdivision(code="AZ-SUS", name="Şuşa", type_="Rayon"),
        AZSubdivision(code="AZ-TAR", name="Tərtər", type_="Rayon"),
        AZSubdivision(code="AZ-TOV", name="Tovuz", type_="Rayon"),
        AZSubdivision(code="AZ-UCA", name="Ucar", type_="Rayon"),
        AZSubdivision(code="AZ-XA", name="Xankəndi", type_="Municipality"),
        AZSubdivision(code="AZ-XAC", name="Xaçmaz", type_="Rayon"),
        AZSubdivision(code="AZ-XCI", name="Xocalı", type_="Rayon"),
        AZSubdivision(code="AZ-XIZ", name="Xızı", type_="Rayon"),
        AZSubdivision(code="AZ-XVD", name="Xocavənd", type_="Rayon"),
        AZSubdivision(code="AZ-YAR", name="Yardımlı", type_="Rayon"),
        AZSubdivision(code="AZ-YE", name="Yevlax", type_="Municipality"),
        AZSubdivision(code="AZ-YEV", name="Yevlax", type_="Rayon"),
        AZSubdivision(code="AZ-ZAN", name="Zəngilan", type_="Rayon"),
        AZSubdivision(code="AZ-ZAQ", name="Zaqatala", type_="Rayon"),
        AZSubdivision(code="AZ-ZAR", name="Zərdab", type_="Rayon"),
    ],
)
