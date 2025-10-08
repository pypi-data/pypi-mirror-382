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

TRSubdivisionCodeType = Literal[
    "TR-01",  # Adana
    "TR-02",  # Adıyaman
    "TR-03",  # Afyonkarahisar
    "TR-04",  # Ağrı
    "TR-05",  # Amasya
    "TR-06",  # Ankara
    "TR-07",  # Antalya
    "TR-08",  # Artvin
    "TR-09",  # Aydın
    "TR-10",  # Balıkesir
    "TR-11",  # Bilecik
    "TR-12",  # Bingöl
    "TR-13",  # Bitlis
    "TR-14",  # Bolu
    "TR-15",  # Burdur
    "TR-16",  # Bursa
    "TR-17",  # Çanakkale
    "TR-18",  # Çankırı
    "TR-19",  # Çorum
    "TR-20",  # Denizli
    "TR-21",  # Diyarbakır
    "TR-22",  # Edirne
    "TR-23",  # Elazığ
    "TR-24",  # Erzincan
    "TR-25",  # Erzurum
    "TR-26",  # Eskişehir
    "TR-27",  # Gaziantep
    "TR-28",  # Giresun
    "TR-29",  # Gümüşhane
    "TR-30",  # Hakkâri
    "TR-31",  # Hatay
    "TR-32",  # Isparta
    "TR-33",  # Mersin
    "TR-34",  # İstanbul
    "TR-35",  # İzmir
    "TR-36",  # Kars
    "TR-37",  # Kastamonu
    "TR-38",  # Kayseri
    "TR-39",  # Kırklareli
    "TR-40",  # Kırşehir
    "TR-41",  # Kocaeli
    "TR-42",  # Konya
    "TR-43",  # Kütahya
    "TR-44",  # Malatya
    "TR-45",  # Manisa
    "TR-46",  # Kahramanmaraş
    "TR-47",  # Mardin
    "TR-48",  # Muğla
    "TR-49",  # Muş
    "TR-50",  # Nevşehir
    "TR-51",  # Niğde
    "TR-52",  # Ordu
    "TR-53",  # Rize
    "TR-54",  # Sakarya
    "TR-55",  # Samsun
    "TR-56",  # Siirt
    "TR-57",  # Sinop
    "TR-58",  # Sivas
    "TR-59",  # Tekirdağ
    "TR-60",  # Tokat
    "TR-61",  # Trabzon
    "TR-62",  # Tunceli
    "TR-63",  # Şanlıurfa
    "TR-64",  # Uşak
    "TR-65",  # Van
    "TR-66",  # Yozgat
    "TR-67",  # Zonguldak
    "TR-68",  # Aksaray
    "TR-69",  # Bayburt
    "TR-70",  # Karaman
    "TR-71",  # Kırıkkale
    "TR-72",  # Batman
    "TR-73",  # Şırnak
    "TR-74",  # Bartın
    "TR-75",  # Ardahan
    "TR-76",  # Iğdır
    "TR-77",  # Yalova
    "TR-78",  # Karabük
    "TR-79",  # Kilis
    "TR-80",  # Osmaniye
    "TR-81",  # Düzce
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class TRSubdivision(Subdivision):
    code: TRSubdivisionCodeType


TR: Final[Country] = Country(
    alpha2="TR",
    alpha3="TUR",
    name="Türkiye",
    common_name=None,
    official_name="Republic of Türkiye",
    subdivisions=[
        TRSubdivision(code="TR-01", name="Adana", type_="Province"),
        TRSubdivision(code="TR-02", name="Adıyaman", type_="Province"),
        TRSubdivision(code="TR-03", name="Afyonkarahisar", type_="Province"),
        TRSubdivision(code="TR-04", name="Ağrı", type_="Province"),
        TRSubdivision(code="TR-05", name="Amasya", type_="Province"),
        TRSubdivision(code="TR-06", name="Ankara", type_="Province"),
        TRSubdivision(code="TR-07", name="Antalya", type_="Province"),
        TRSubdivision(code="TR-08", name="Artvin", type_="Province"),
        TRSubdivision(code="TR-09", name="Aydın", type_="Province"),
        TRSubdivision(code="TR-10", name="Balıkesir", type_="Province"),
        TRSubdivision(code="TR-11", name="Bilecik", type_="Province"),
        TRSubdivision(code="TR-12", name="Bingöl", type_="Province"),
        TRSubdivision(code="TR-13", name="Bitlis", type_="Province"),
        TRSubdivision(code="TR-14", name="Bolu", type_="Province"),
        TRSubdivision(code="TR-15", name="Burdur", type_="Province"),
        TRSubdivision(code="TR-16", name="Bursa", type_="Province"),
        TRSubdivision(code="TR-17", name="Çanakkale", type_="Province"),
        TRSubdivision(code="TR-18", name="Çankırı", type_="Province"),
        TRSubdivision(code="TR-19", name="Çorum", type_="Province"),
        TRSubdivision(code="TR-20", name="Denizli", type_="Province"),
        TRSubdivision(code="TR-21", name="Diyarbakır", type_="Province"),
        TRSubdivision(code="TR-22", name="Edirne", type_="Province"),
        TRSubdivision(code="TR-23", name="Elazığ", type_="Province"),
        TRSubdivision(code="TR-24", name="Erzincan", type_="Province"),
        TRSubdivision(code="TR-25", name="Erzurum", type_="Province"),
        TRSubdivision(code="TR-26", name="Eskişehir", type_="Province"),
        TRSubdivision(code="TR-27", name="Gaziantep", type_="Province"),
        TRSubdivision(code="TR-28", name="Giresun", type_="Province"),
        TRSubdivision(code="TR-29", name="Gümüşhane", type_="Province"),
        TRSubdivision(code="TR-30", name="Hakkâri", type_="Province"),
        TRSubdivision(code="TR-31", name="Hatay", type_="Province"),
        TRSubdivision(code="TR-32", name="Isparta", type_="Province"),
        TRSubdivision(code="TR-33", name="Mersin", type_="Province"),
        TRSubdivision(code="TR-34", name="İstanbul", type_="Province"),
        TRSubdivision(code="TR-35", name="İzmir", type_="Province"),
        TRSubdivision(code="TR-36", name="Kars", type_="Province"),
        TRSubdivision(code="TR-37", name="Kastamonu", type_="Province"),
        TRSubdivision(code="TR-38", name="Kayseri", type_="Province"),
        TRSubdivision(code="TR-39", name="Kırklareli", type_="Province"),
        TRSubdivision(code="TR-40", name="Kırşehir", type_="Province"),
        TRSubdivision(code="TR-41", name="Kocaeli", type_="Province"),
        TRSubdivision(code="TR-42", name="Konya", type_="Province"),
        TRSubdivision(code="TR-43", name="Kütahya", type_="Province"),
        TRSubdivision(code="TR-44", name="Malatya", type_="Province"),
        TRSubdivision(code="TR-45", name="Manisa", type_="Province"),
        TRSubdivision(code="TR-46", name="Kahramanmaraş", type_="Province"),
        TRSubdivision(code="TR-47", name="Mardin", type_="Province"),
        TRSubdivision(code="TR-48", name="Muğla", type_="Province"),
        TRSubdivision(code="TR-49", name="Muş", type_="Province"),
        TRSubdivision(code="TR-50", name="Nevşehir", type_="Province"),
        TRSubdivision(code="TR-51", name="Niğde", type_="Province"),
        TRSubdivision(code="TR-52", name="Ordu", type_="Province"),
        TRSubdivision(code="TR-53", name="Rize", type_="Province"),
        TRSubdivision(code="TR-54", name="Sakarya", type_="Province"),
        TRSubdivision(code="TR-55", name="Samsun", type_="Province"),
        TRSubdivision(code="TR-56", name="Siirt", type_="Province"),
        TRSubdivision(code="TR-57", name="Sinop", type_="Province"),
        TRSubdivision(code="TR-58", name="Sivas", type_="Province"),
        TRSubdivision(code="TR-59", name="Tekirdağ", type_="Province"),
        TRSubdivision(code="TR-60", name="Tokat", type_="Province"),
        TRSubdivision(code="TR-61", name="Trabzon", type_="Province"),
        TRSubdivision(code="TR-62", name="Tunceli", type_="Province"),
        TRSubdivision(code="TR-63", name="Şanlıurfa", type_="Province"),
        TRSubdivision(code="TR-64", name="Uşak", type_="Province"),
        TRSubdivision(code="TR-65", name="Van", type_="Province"),
        TRSubdivision(code="TR-66", name="Yozgat", type_="Province"),
        TRSubdivision(code="TR-67", name="Zonguldak", type_="Province"),
        TRSubdivision(code="TR-68", name="Aksaray", type_="Province"),
        TRSubdivision(code="TR-69", name="Bayburt", type_="Province"),
        TRSubdivision(code="TR-70", name="Karaman", type_="Province"),
        TRSubdivision(code="TR-71", name="Kırıkkale", type_="Province"),
        TRSubdivision(code="TR-72", name="Batman", type_="Province"),
        TRSubdivision(code="TR-73", name="Şırnak", type_="Province"),
        TRSubdivision(code="TR-74", name="Bartın", type_="Province"),
        TRSubdivision(code="TR-75", name="Ardahan", type_="Province"),
        TRSubdivision(code="TR-76", name="Iğdır", type_="Province"),
        TRSubdivision(code="TR-77", name="Yalova", type_="Province"),
        TRSubdivision(code="TR-78", name="Karabük", type_="Province"),
        TRSubdivision(code="TR-79", name="Kilis", type_="Province"),
        TRSubdivision(code="TR-80", name="Osmaniye", type_="Province"),
        TRSubdivision(code="TR-81", name="Düzce", type_="Province"),
    ],
)
