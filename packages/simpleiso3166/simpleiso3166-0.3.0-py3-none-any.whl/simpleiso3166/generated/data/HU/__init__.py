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

HUSubdivisionCodeType = Literal[
    "HU-BA",  # Baranya
    "HU-BC",  # Békéscsaba
    "HU-BE",  # Békés
    "HU-BK",  # Bács-Kiskun
    "HU-BU",  # Budapest
    "HU-BZ",  # Borsod-Abaúj-Zemplén
    "HU-CS",  # Csongrád-Csanád
    "HU-DE",  # Debrecen
    "HU-DU",  # Dunaújváros
    "HU-EG",  # Eger
    "HU-ER",  # Érd
    "HU-FE",  # Fejér
    "HU-GS",  # Győr-Moson-Sopron
    "HU-GY",  # Győr
    "HU-HB",  # Hajdú-Bihar
    "HU-HE",  # Heves
    "HU-HV",  # Hódmezővásárhely
    "HU-JN",  # Jász-Nagykun-Szolnok
    "HU-KE",  # Komárom-Esztergom
    "HU-KM",  # Kecskemét
    "HU-KV",  # Kaposvár
    "HU-MI",  # Miskolc
    "HU-NK",  # Nagykanizsa
    "HU-NO",  # Nógrád
    "HU-NY",  # Nyíregyháza
    "HU-PE",  # Pest
    "HU-PS",  # Pécs
    "HU-SD",  # Szeged
    "HU-SF",  # Székesfehérvár
    "HU-SH",  # Szombathely
    "HU-SK",  # Szolnok
    "HU-SN",  # Sopron
    "HU-SO",  # Somogy
    "HU-SS",  # Szekszárd
    "HU-ST",  # Salgótarján
    "HU-SZ",  # Szabolcs-Szatmár-Bereg
    "HU-TB",  # Tatabánya
    "HU-TO",  # Tolna
    "HU-VA",  # Vas
    "HU-VE",  # Veszprém
    "HU-VM",  # Veszprém
    "HU-ZA",  # Zala
    "HU-ZE",  # Zalaegerszeg
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class HUSubdivision(Subdivision):
    code: HUSubdivisionCodeType


HU: Final[Country] = Country(
    alpha2="HU",
    alpha3="HUN",
    name="Hungary",
    common_name=None,
    official_name="Hungary",
    subdivisions=[
        HUSubdivision(code="HU-BA", name="Baranya", type_="County"),
        HUSubdivision(code="HU-BC", name="Békéscsaba", type_="City with county rights"),
        HUSubdivision(code="HU-BE", name="Békés", type_="County"),
        HUSubdivision(code="HU-BK", name="Bács-Kiskun", type_="County"),
        HUSubdivision(code="HU-BU", name="Budapest", type_="Capital city"),
        HUSubdivision(code="HU-BZ", name="Borsod-Abaúj-Zemplén", type_="County"),
        HUSubdivision(code="HU-CS", name="Csongrád-Csanád", type_="County"),
        HUSubdivision(code="HU-DE", name="Debrecen", type_="City with county rights"),
        HUSubdivision(code="HU-DU", name="Dunaújváros", type_="City with county rights"),
        HUSubdivision(code="HU-EG", name="Eger", type_="City with county rights"),
        HUSubdivision(code="HU-ER", name="Érd", type_="City with county rights"),
        HUSubdivision(code="HU-FE", name="Fejér", type_="County"),
        HUSubdivision(code="HU-GS", name="Győr-Moson-Sopron", type_="County"),
        HUSubdivision(code="HU-GY", name="Győr", type_="City with county rights"),
        HUSubdivision(code="HU-HB", name="Hajdú-Bihar", type_="County"),
        HUSubdivision(code="HU-HE", name="Heves", type_="County"),
        HUSubdivision(code="HU-HV", name="Hódmezővásárhely", type_="City with county rights"),
        HUSubdivision(code="HU-JN", name="Jász-Nagykun-Szolnok", type_="County"),
        HUSubdivision(code="HU-KE", name="Komárom-Esztergom", type_="County"),
        HUSubdivision(code="HU-KM", name="Kecskemét", type_="City with county rights"),
        HUSubdivision(code="HU-KV", name="Kaposvár", type_="City with county rights"),
        HUSubdivision(code="HU-MI", name="Miskolc", type_="City with county rights"),
        HUSubdivision(code="HU-NK", name="Nagykanizsa", type_="City with county rights"),
        HUSubdivision(code="HU-NO", name="Nógrád", type_="County"),
        HUSubdivision(code="HU-NY", name="Nyíregyháza", type_="City with county rights"),
        HUSubdivision(code="HU-PE", name="Pest", type_="County"),
        HUSubdivision(code="HU-PS", name="Pécs", type_="City with county rights"),
        HUSubdivision(code="HU-SD", name="Szeged", type_="City with county rights"),
        HUSubdivision(code="HU-SF", name="Székesfehérvár", type_="City with county rights"),
        HUSubdivision(code="HU-SH", name="Szombathely", type_="City with county rights"),
        HUSubdivision(code="HU-SK", name="Szolnok", type_="City with county rights"),
        HUSubdivision(code="HU-SN", name="Sopron", type_="City with county rights"),
        HUSubdivision(code="HU-SO", name="Somogy", type_="County"),
        HUSubdivision(code="HU-SS", name="Szekszárd", type_="City with county rights"),
        HUSubdivision(code="HU-ST", name="Salgótarján", type_="City with county rights"),
        HUSubdivision(code="HU-SZ", name="Szabolcs-Szatmár-Bereg", type_="County"),
        HUSubdivision(code="HU-TB", name="Tatabánya", type_="City with county rights"),
        HUSubdivision(code="HU-TO", name="Tolna", type_="County"),
        HUSubdivision(code="HU-VA", name="Vas", type_="County"),
        HUSubdivision(code="HU-VE", name="Veszprém", type_="County"),
        HUSubdivision(code="HU-VM", name="Veszprém", type_="City with county rights"),
        HUSubdivision(code="HU-ZA", name="Zala", type_="County"),
        HUSubdivision(code="HU-ZE", name="Zalaegerszeg", type_="City with county rights"),
    ],
)
