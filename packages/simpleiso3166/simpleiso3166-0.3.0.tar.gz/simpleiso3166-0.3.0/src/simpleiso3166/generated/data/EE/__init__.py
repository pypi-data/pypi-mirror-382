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

EESubdivisionCodeType = Literal[
    "EE-130",  # Alutaguse
    "EE-141",  # Anija
    "EE-142",  # Antsla
    "EE-171",  # Elva
    "EE-184",  # Haapsalu
    "EE-191",  # Haljala
    "EE-198",  # Harku
    "EE-205",  # Hiiumaa
    "EE-214",  # Häädemeeste
    "EE-245",  # Jõelähtme
    "EE-247",  # Jõgeva
    "EE-251",  # Jõhvi
    "EE-255",  # Järva
    "EE-272",  # Kadrina
    "EE-283",  # Kambja
    "EE-284",  # Kanepi
    "EE-291",  # Kastre
    "EE-293",  # Kehtna
    "EE-296",  # Keila
    "EE-303",  # Kihnu
    "EE-305",  # Kiili
    "EE-317",  # Kohila
    "EE-321",  # Kohtla-Järve
    "EE-338",  # Kose
    "EE-353",  # Kuusalu
    "EE-37",  # Harjumaa
    "EE-39",  # Hiiumaa
    "EE-424",  # Loksa
    "EE-430",  # Lääneranna
    "EE-431",  # Lääne-Harju
    "EE-432",  # Luunja
    "EE-441",  # Lääne-Nigula
    "EE-442",  # Lüganuse
    "EE-446",  # Maardu
    "EE-45",  # Ida-Virumaa
    "EE-478",  # Muhu
    "EE-480",  # Mulgi
    "EE-486",  # Mustvee
    "EE-50",  # Jõgevamaa
    "EE-503",  # Märjamaa
    "EE-511",  # Narva
    "EE-514",  # Narva-Jõesuu
    "EE-52",  # Järvamaa
    "EE-528",  # Nõo
    "EE-557",  # Otepää
    "EE-56",  # Läänemaa
    "EE-567",  # Paide
    "EE-586",  # Peipsiääre
    "EE-60",  # Lääne-Virumaa
    "EE-615",  # Põhja-Sakala
    "EE-618",  # Põltsamaa
    "EE-622",  # Põlva
    "EE-624",  # Pärnu
    "EE-638",  # Põhja-Pärnumaa
    "EE-64",  # Põlvamaa
    "EE-651",  # Raasiku
    "EE-653",  # Rae
    "EE-661",  # Rakvere
    "EE-663",  # Rakvere
    "EE-668",  # Rapla
    "EE-68",  # Pärnumaa
    "EE-689",  # Ruhnu
    "EE-698",  # Rõuge
    "EE-708",  # Räpina
    "EE-71",  # Raplamaa
    "EE-712",  # Saarde
    "EE-714",  # Saaremaa
    "EE-719",  # Saku
    "EE-726",  # Saue
    "EE-732",  # Setomaa
    "EE-735",  # Sillamäe
    "EE-74",  # Saaremaa
    "EE-784",  # Tallinn
    "EE-79",  # Tartumaa
    "EE-792",  # Tapa
    "EE-793",  # Tartu
    "EE-796",  # Tartu
    "EE-803",  # Toila
    "EE-809",  # Tori
    "EE-81",  # Valgamaa
    "EE-824",  # Tõrva
    "EE-834",  # Türi
    "EE-84",  # Viljandimaa
    "EE-855",  # Valga
    "EE-87",  # Võrumaa
    "EE-890",  # Viimsi
    "EE-897",  # Viljandi
    "EE-899",  # Viljandi
    "EE-901",  # Vinni
    "EE-903",  # Viru-Nigula
    "EE-907",  # Vormsi
    "EE-917",  # Võru
    "EE-919",  # Võru
    "EE-928",  # Väike-Maarja
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class EESubdivision(Subdivision):
    code: EESubdivisionCodeType


EE: Final[Country] = Country(
    alpha2="EE",
    alpha3="EST",
    name="Estonia",
    common_name=None,
    official_name="Republic of Estonia",
    subdivisions=[
        EESubdivision(code="EE-130", name="Alutaguse", type_="Rural municipality"),
        EESubdivision(code="EE-141", name="Anija", type_="Rural municipality"),
        EESubdivision(code="EE-142", name="Antsla", type_="Rural municipality"),
        EESubdivision(code="EE-171", name="Elva", type_="Rural municipality"),
        EESubdivision(code="EE-184", name="Haapsalu", type_="Urban municipality"),
        EESubdivision(code="EE-191", name="Haljala", type_="Rural municipality"),
        EESubdivision(code="EE-198", name="Harku", type_="Rural municipality"),
        EESubdivision(code="EE-205", name="Hiiumaa", type_="Rural municipality"),
        EESubdivision(code="EE-214", name="Häädemeeste", type_="Rural municipality"),
        EESubdivision(code="EE-245", name="Jõelähtme", type_="Rural municipality"),
        EESubdivision(code="EE-247", name="Jõgeva", type_="Rural municipality"),
        EESubdivision(code="EE-251", name="Jõhvi", type_="Rural municipality"),
        EESubdivision(code="EE-255", name="Järva", type_="Rural municipality"),
        EESubdivision(code="EE-272", name="Kadrina", type_="Rural municipality"),
        EESubdivision(code="EE-283", name="Kambja", type_="Rural municipality"),
        EESubdivision(code="EE-284", name="Kanepi", type_="Rural municipality"),
        EESubdivision(code="EE-291", name="Kastre", type_="Rural municipality"),
        EESubdivision(code="EE-293", name="Kehtna", type_="Rural municipality"),
        EESubdivision(code="EE-296", name="Keila", type_="Urban municipality"),
        EESubdivision(code="EE-303", name="Kihnu", type_="Rural municipality"),
        EESubdivision(code="EE-305", name="Kiili", type_="Rural municipality"),
        EESubdivision(code="EE-317", name="Kohila", type_="Rural municipality"),
        EESubdivision(code="EE-321", name="Kohtla-Järve", type_="Urban municipality"),
        EESubdivision(code="EE-338", name="Kose", type_="Rural municipality"),
        EESubdivision(code="EE-353", name="Kuusalu", type_="Rural municipality"),
        EESubdivision(code="EE-37", name="Harjumaa", type_="County"),
        EESubdivision(code="EE-39", name="Hiiumaa", type_="County"),
        EESubdivision(code="EE-424", name="Loksa", type_="Urban municipality"),
        EESubdivision(code="EE-430", name="Lääneranna", type_="Rural municipality"),
        EESubdivision(code="EE-431", name="Lääne-Harju", type_="Rural municipality"),
        EESubdivision(code="EE-432", name="Luunja", type_="Rural municipality"),
        EESubdivision(code="EE-441", name="Lääne-Nigula", type_="Rural municipality"),
        EESubdivision(code="EE-442", name="Lüganuse", type_="Rural municipality"),
        EESubdivision(code="EE-446", name="Maardu", type_="Urban municipality"),
        EESubdivision(code="EE-45", name="Ida-Virumaa", type_="County"),
        EESubdivision(code="EE-478", name="Muhu", type_="Rural municipality"),
        EESubdivision(code="EE-480", name="Mulgi", type_="Rural municipality"),
        EESubdivision(code="EE-486", name="Mustvee", type_="Rural municipality"),
        EESubdivision(code="EE-50", name="Jõgevamaa", type_="County"),
        EESubdivision(code="EE-503", name="Märjamaa", type_="Rural municipality"),
        EESubdivision(code="EE-511", name="Narva", type_="Urban municipality"),
        EESubdivision(code="EE-514", name="Narva-Jõesuu", type_="Urban municipality"),
        EESubdivision(code="EE-52", name="Järvamaa", type_="County"),
        EESubdivision(code="EE-528", name="Nõo", type_="Rural municipality"),
        EESubdivision(code="EE-557", name="Otepää", type_="Rural municipality"),
        EESubdivision(code="EE-56", name="Läänemaa", type_="County"),
        EESubdivision(code="EE-567", name="Paide", type_="Urban municipality"),
        EESubdivision(code="EE-586", name="Peipsiääre", type_="Rural municipality"),
        EESubdivision(code="EE-60", name="Lääne-Virumaa", type_="County"),
        EESubdivision(code="EE-615", name="Põhja-Sakala", type_="Rural municipality"),
        EESubdivision(code="EE-618", name="Põltsamaa", type_="Rural municipality"),
        EESubdivision(code="EE-622", name="Põlva", type_="Rural municipality"),
        EESubdivision(code="EE-624", name="Pärnu", type_="Urban municipality"),
        EESubdivision(code="EE-638", name="Põhja-Pärnumaa", type_="Rural municipality"),
        EESubdivision(code="EE-64", name="Põlvamaa", type_="County"),
        EESubdivision(code="EE-651", name="Raasiku", type_="Rural municipality"),
        EESubdivision(code="EE-653", name="Rae", type_="Rural municipality"),
        EESubdivision(code="EE-661", name="Rakvere", type_="Rural municipality"),
        EESubdivision(code="EE-663", name="Rakvere", type_="Urban municipality"),
        EESubdivision(code="EE-668", name="Rapla", type_="Rural municipality"),
        EESubdivision(code="EE-68", name="Pärnumaa", type_="County"),
        EESubdivision(code="EE-689", name="Ruhnu", type_="Rural municipality"),
        EESubdivision(code="EE-698", name="Rõuge", type_="Rural municipality"),
        EESubdivision(code="EE-708", name="Räpina", type_="Rural municipality"),
        EESubdivision(code="EE-71", name="Raplamaa", type_="County"),
        EESubdivision(code="EE-712", name="Saarde", type_="Rural municipality"),
        EESubdivision(code="EE-714", name="Saaremaa", type_="Rural municipality"),
        EESubdivision(code="EE-719", name="Saku", type_="Rural municipality"),
        EESubdivision(code="EE-726", name="Saue", type_="Rural municipality"),
        EESubdivision(code="EE-732", name="Setomaa", type_="Rural municipality"),
        EESubdivision(code="EE-735", name="Sillamäe", type_="Urban municipality"),
        EESubdivision(code="EE-74", name="Saaremaa", type_="County"),
        EESubdivision(code="EE-784", name="Tallinn", type_="Urban municipality"),
        EESubdivision(code="EE-79", name="Tartumaa", type_="County"),
        EESubdivision(code="EE-792", name="Tapa", type_="Rural municipality"),
        EESubdivision(code="EE-793", name="Tartu", type_="Urban municipality"),
        EESubdivision(code="EE-796", name="Tartu", type_="Rural municipality"),
        EESubdivision(code="EE-803", name="Toila", type_="Rural municipality"),
        EESubdivision(code="EE-809", name="Tori", type_="Rural municipality"),
        EESubdivision(code="EE-81", name="Valgamaa", type_="County"),
        EESubdivision(code="EE-824", name="Tõrva", type_="Rural municipality"),
        EESubdivision(code="EE-834", name="Türi", type_="Rural municipality"),
        EESubdivision(code="EE-84", name="Viljandimaa", type_="County"),
        EESubdivision(code="EE-855", name="Valga", type_="Rural municipality"),
        EESubdivision(code="EE-87", name="Võrumaa", type_="County"),
        EESubdivision(code="EE-890", name="Viimsi", type_="Rural municipality"),
        EESubdivision(code="EE-897", name="Viljandi", type_="Urban municipality"),
        EESubdivision(code="EE-899", name="Viljandi", type_="Rural municipality"),
        EESubdivision(code="EE-901", name="Vinni", type_="Rural municipality"),
        EESubdivision(code="EE-903", name="Viru-Nigula", type_="Rural municipality"),
        EESubdivision(code="EE-907", name="Vormsi", type_="Rural municipality"),
        EESubdivision(code="EE-917", name="Võru", type_="Rural municipality"),
        EESubdivision(code="EE-919", name="Võru", type_="Urban municipality"),
        EESubdivision(code="EE-928", name="Väike-Maarja", type_="Rural municipality"),
    ],
)
