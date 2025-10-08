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

IDSubdivisionCodeType = Literal[
    "ID-AC",  # Aceh
    "ID-BA",  # Bali
    "ID-BB",  # Kepulauan Bangka Belitung
    "ID-BE",  # Bengkulu
    "ID-BT",  # Banten
    "ID-GO",  # Gorontalo
    "ID-JA",  # Jambi
    "ID-JB",  # Jawa Barat
    "ID-JI",  # Jawa Timur
    "ID-JK",  # Jakarta Raya
    "ID-JT",  # Jawa Tengah
    "ID-JW",  # Jawa
    "ID-KA",  # Kalimantan
    "ID-KB",  # Kalimantan Barat
    "ID-KI",  # Kalimantan Timur
    "ID-KR",  # Kepulauan Riau
    "ID-KS",  # Kalimantan Selatan
    "ID-KT",  # Kalimantan Tengah
    "ID-KU",  # Kalimantan Utara
    "ID-LA",  # Lampung
    "ID-MA",  # Maluku
    "ID-ML",  # Maluku
    "ID-MU",  # Maluku Utara
    "ID-NB",  # Nusa Tenggara Barat
    "ID-NT",  # Nusa Tenggara Timur
    "ID-NU",  # Nusa Tenggara
    "ID-PA",  # Papua
    "ID-PB",  # Papua Barat
    "ID-PD",  # Papua Barat Daya
    "ID-PE",  # Papua Pengunungan
    "ID-PP",  # Papua
    "ID-PS",  # Papua Selatan
    "ID-PT",  # Papua Tengah
    "ID-RI",  # Riau
    "ID-SA",  # Sulawesi Utara
    "ID-SB",  # Sumatera Barat
    "ID-SG",  # Sulawesi Tenggara
    "ID-SL",  # Sulawesi
    "ID-SM",  # Sumatera
    "ID-SN",  # Sulawesi Selatan
    "ID-SR",  # Sulawesi Barat
    "ID-SS",  # Sumatera Selatan
    "ID-ST",  # Sulawesi Tengah
    "ID-SU",  # Sumatera Utara
    "ID-YO",  # Yogyakarta
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class IDSubdivision(Subdivision):
    code: IDSubdivisionCodeType


ID: Final[Country] = Country(
    alpha2="ID",
    alpha3="IDN",
    name="Indonesia",
    common_name=None,
    official_name="Republic of Indonesia",
    subdivisions=[
        IDSubdivision(code="ID-AC", name="Aceh", type_="Province"),
        IDSubdivision(code="ID-BA", name="Bali", type_="Province"),
        IDSubdivision(code="ID-BB", name="Kepulauan Bangka Belitung", type_="Province"),
        IDSubdivision(code="ID-BE", name="Bengkulu", type_="Province"),
        IDSubdivision(code="ID-BT", name="Banten", type_="Province"),
        IDSubdivision(code="ID-GO", name="Gorontalo", type_="Province"),
        IDSubdivision(code="ID-JA", name="Jambi", type_="Province"),
        IDSubdivision(code="ID-JB", name="Jawa Barat", type_="Province"),
        IDSubdivision(code="ID-JI", name="Jawa Timur", type_="Province"),
        IDSubdivision(code="ID-JK", name="Jakarta Raya", type_="Capital district"),
        IDSubdivision(code="ID-JT", name="Jawa Tengah", type_="Province"),
        IDSubdivision(code="ID-JW", name="Jawa", type_="Geographical unit"),
        IDSubdivision(code="ID-KA", name="Kalimantan", type_="Geographical unit"),
        IDSubdivision(code="ID-KB", name="Kalimantan Barat", type_="Province"),
        IDSubdivision(code="ID-KI", name="Kalimantan Timur", type_="Province"),
        IDSubdivision(code="ID-KR", name="Kepulauan Riau", type_="Province"),
        IDSubdivision(code="ID-KS", name="Kalimantan Selatan", type_="Province"),
        IDSubdivision(code="ID-KT", name="Kalimantan Tengah", type_="Province"),
        IDSubdivision(code="ID-KU", name="Kalimantan Utara", type_="Province"),
        IDSubdivision(code="ID-LA", name="Lampung", type_="Province"),
        IDSubdivision(code="ID-MA", name="Maluku", type_="Province"),
        IDSubdivision(code="ID-ML", name="Maluku", type_="Geographical unit"),
        IDSubdivision(code="ID-MU", name="Maluku Utara", type_="Province"),
        IDSubdivision(code="ID-NB", name="Nusa Tenggara Barat", type_="Province"),
        IDSubdivision(code="ID-NT", name="Nusa Tenggara Timur", type_="Province"),
        IDSubdivision(code="ID-NU", name="Nusa Tenggara", type_="Geographical unit"),
        IDSubdivision(code="ID-PA", name="Papua", type_="Province"),
        IDSubdivision(code="ID-PB", name="Papua Barat", type_="Province"),
        IDSubdivision(code="ID-PD", name="Papua Barat Daya", type_="Province"),
        IDSubdivision(code="ID-PE", name="Papua Pengunungan", type_="Province"),
        IDSubdivision(code="ID-PP", name="Papua", type_="Geographical unit"),
        IDSubdivision(code="ID-PS", name="Papua Selatan", type_="Province"),
        IDSubdivision(code="ID-PT", name="Papua Tengah", type_="Province"),
        IDSubdivision(code="ID-RI", name="Riau", type_="Province"),
        IDSubdivision(code="ID-SA", name="Sulawesi Utara", type_="Province"),
        IDSubdivision(code="ID-SB", name="Sumatera Barat", type_="Province"),
        IDSubdivision(code="ID-SG", name="Sulawesi Tenggara", type_="Province"),
        IDSubdivision(code="ID-SL", name="Sulawesi", type_="Geographical unit"),
        IDSubdivision(code="ID-SM", name="Sumatera", type_="Geographical unit"),
        IDSubdivision(code="ID-SN", name="Sulawesi Selatan", type_="Province"),
        IDSubdivision(code="ID-SR", name="Sulawesi Barat", type_="Province"),
        IDSubdivision(code="ID-SS", name="Sumatera Selatan", type_="Province"),
        IDSubdivision(code="ID-ST", name="Sulawesi Tengah", type_="Province"),
        IDSubdivision(code="ID-SU", name="Sumatera Utara", type_="Province"),
        IDSubdivision(code="ID-YO", name="Yogyakarta", type_="Special region"),
    ],
)
