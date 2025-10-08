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

UGSubdivisionCodeType = Literal[
    "UG-101",  # Kalangala
    "UG-102",  # Kampala
    "UG-103",  # Kiboga
    "UG-104",  # Luwero
    "UG-105",  # Masaka
    "UG-106",  # Mpigi
    "UG-107",  # Mubende
    "UG-108",  # Mukono
    "UG-109",  # Nakasongola
    "UG-110",  # Rakai
    "UG-111",  # Sembabule
    "UG-112",  # Kayunga
    "UG-113",  # Wakiso
    "UG-114",  # Lyantonde
    "UG-115",  # Mityana
    "UG-116",  # Nakaseke
    "UG-117",  # Buikwe
    "UG-118",  # Bukomansibi
    "UG-119",  # Butambala
    "UG-120",  # Buvuma
    "UG-121",  # Gomba
    "UG-122",  # Kalungu
    "UG-123",  # Kyankwanzi
    "UG-124",  # Lwengo
    "UG-125",  # Kyotera
    "UG-126",  # Kasanda
    "UG-201",  # Bugiri
    "UG-202",  # Busia
    "UG-203",  # Iganga
    "UG-204",  # Jinja
    "UG-205",  # Kamuli
    "UG-206",  # Kapchorwa
    "UG-207",  # Katakwi
    "UG-208",  # Kumi
    "UG-209",  # Mbale
    "UG-210",  # Pallisa
    "UG-211",  # Soroti
    "UG-212",  # Tororo
    "UG-213",  # Kaberamaido
    "UG-214",  # Mayuge
    "UG-215",  # Sironko
    "UG-216",  # Amuria
    "UG-217",  # Budaka
    "UG-218",  # Bududa
    "UG-219",  # Bukedea
    "UG-220",  # Bukwo
    "UG-221",  # Butaleja
    "UG-222",  # Kaliro
    "UG-223",  # Manafwa
    "UG-224",  # Namutumba
    "UG-225",  # Bulambuli
    "UG-226",  # Buyende
    "UG-227",  # Kibuku
    "UG-228",  # Kween
    "UG-229",  # Luuka
    "UG-230",  # Namayingo
    "UG-231",  # Ngora
    "UG-232",  # Serere
    "UG-233",  # Butebo
    "UG-234",  # Namisindwa
    "UG-235",  # Bugweri
    "UG-236",  # Kapelebyong
    "UG-237",  # Kalaki
    "UG-301",  # Adjumani
    "UG-302",  # Apac
    "UG-303",  # Arua
    "UG-304",  # Gulu
    "UG-305",  # Kitgum
    "UG-306",  # Kotido
    "UG-307",  # Lira
    "UG-308",  # Moroto
    "UG-309",  # Moyo
    "UG-310",  # Nebbi
    "UG-311",  # Nakapiripirit
    "UG-312",  # Pader
    "UG-313",  # Yumbe
    "UG-314",  # Abim
    "UG-315",  # Amolatar
    "UG-316",  # Amuru
    "UG-317",  # Dokolo
    "UG-318",  # Kaabong
    "UG-319",  # Koboko
    "UG-320",  # Maracha
    "UG-321",  # Oyam
    "UG-322",  # Agago
    "UG-323",  # Alebtong
    "UG-324",  # Amudat
    "UG-325",  # Kole
    "UG-326",  # Lamwo
    "UG-327",  # Napak
    "UG-328",  # Nwoya
    "UG-329",  # Otuke
    "UG-330",  # Zombo
    "UG-331",  # Omoro
    "UG-332",  # Pakwach
    "UG-333",  # Kwania
    "UG-334",  # Nabilatuk
    "UG-335",  # Karenga
    "UG-336",  # Madi-Okollo
    "UG-337",  # Obongi
    "UG-401",  # Bundibugyo
    "UG-402",  # Bushenyi
    "UG-403",  # Hoima
    "UG-404",  # Kabale
    "UG-405",  # Kabarole
    "UG-406",  # Kasese
    "UG-407",  # Kibaale
    "UG-408",  # Kisoro
    "UG-409",  # Masindi
    "UG-410",  # Mbarara
    "UG-411",  # Ntungamo
    "UG-412",  # Rukungiri
    "UG-413",  # Kamwenge
    "UG-414",  # Kanungu
    "UG-415",  # Kyenjojo
    "UG-416",  # Buliisa
    "UG-417",  # Ibanda
    "UG-418",  # Isingiro
    "UG-419",  # Kiruhura
    "UG-420",  # Buhweju
    "UG-421",  # Kiryandongo
    "UG-422",  # Kyegegwa
    "UG-423",  # Mitooma
    "UG-424",  # Ntoroko
    "UG-425",  # Rubirizi
    "UG-426",  # Sheema
    "UG-427",  # Kagadi
    "UG-428",  # Kakumiro
    "UG-429",  # Rubanda
    "UG-430",  # Bunyangabu
    "UG-431",  # Rukiga
    "UG-432",  # Kikuube
    "UG-433",  # Kazo
    "UG-434",  # Kitagwenda
    "UG-435",  # Rwampara
    "UG-C",  # Central
    "UG-E",  # Eastern
    "UG-N",  # Northern
    "UG-W",  # Western
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class UGSubdivision(Subdivision):
    code: UGSubdivisionCodeType


UG: Final[Country] = Country(
    alpha2="UG",
    alpha3="UGA",
    name="Uganda",
    common_name=None,
    official_name="Republic of Uganda",
    subdivisions=[
        UGSubdivision(code="UG-101", name="Kalangala", type_="District"),
        UGSubdivision(code="UG-102", name="Kampala", type_="City"),
        UGSubdivision(code="UG-103", name="Kiboga", type_="District"),
        UGSubdivision(code="UG-104", name="Luwero", type_="District"),
        UGSubdivision(code="UG-105", name="Masaka", type_="District"),
        UGSubdivision(code="UG-106", name="Mpigi", type_="District"),
        UGSubdivision(code="UG-107", name="Mubende", type_="District"),
        UGSubdivision(code="UG-108", name="Mukono", type_="District"),
        UGSubdivision(code="UG-109", name="Nakasongola", type_="District"),
        UGSubdivision(code="UG-110", name="Rakai", type_="District"),
        UGSubdivision(code="UG-111", name="Sembabule", type_="District"),
        UGSubdivision(code="UG-112", name="Kayunga", type_="District"),
        UGSubdivision(code="UG-113", name="Wakiso", type_="District"),
        UGSubdivision(code="UG-114", name="Lyantonde", type_="District"),
        UGSubdivision(code="UG-115", name="Mityana", type_="District"),
        UGSubdivision(code="UG-116", name="Nakaseke", type_="District"),
        UGSubdivision(code="UG-117", name="Buikwe", type_="District"),
        UGSubdivision(code="UG-118", name="Bukomansibi", type_="District"),
        UGSubdivision(code="UG-119", name="Butambala", type_="District"),
        UGSubdivision(code="UG-120", name="Buvuma", type_="District"),
        UGSubdivision(code="UG-121", name="Gomba", type_="District"),
        UGSubdivision(code="UG-122", name="Kalungu", type_="District"),
        UGSubdivision(code="UG-123", name="Kyankwanzi", type_="District"),
        UGSubdivision(code="UG-124", name="Lwengo", type_="District"),
        UGSubdivision(code="UG-125", name="Kyotera", type_="District"),
        UGSubdivision(code="UG-126", name="Kasanda", type_="District"),
        UGSubdivision(code="UG-201", name="Bugiri", type_="District"),
        UGSubdivision(code="UG-202", name="Busia", type_="District"),
        UGSubdivision(code="UG-203", name="Iganga", type_="District"),
        UGSubdivision(code="UG-204", name="Jinja", type_="District"),
        UGSubdivision(code="UG-205", name="Kamuli", type_="District"),
        UGSubdivision(code="UG-206", name="Kapchorwa", type_="District"),
        UGSubdivision(code="UG-207", name="Katakwi", type_="District"),
        UGSubdivision(code="UG-208", name="Kumi", type_="District"),
        UGSubdivision(code="UG-209", name="Mbale", type_="District"),
        UGSubdivision(code="UG-210", name="Pallisa", type_="District"),
        UGSubdivision(code="UG-211", name="Soroti", type_="District"),
        UGSubdivision(code="UG-212", name="Tororo", type_="District"),
        UGSubdivision(code="UG-213", name="Kaberamaido", type_="District"),
        UGSubdivision(code="UG-214", name="Mayuge", type_="District"),
        UGSubdivision(code="UG-215", name="Sironko", type_="District"),
        UGSubdivision(code="UG-216", name="Amuria", type_="District"),
        UGSubdivision(code="UG-217", name="Budaka", type_="District"),
        UGSubdivision(code="UG-218", name="Bududa", type_="District"),
        UGSubdivision(code="UG-219", name="Bukedea", type_="District"),
        UGSubdivision(code="UG-220", name="Bukwo", type_="District"),
        UGSubdivision(code="UG-221", name="Butaleja", type_="District"),
        UGSubdivision(code="UG-222", name="Kaliro", type_="District"),
        UGSubdivision(code="UG-223", name="Manafwa", type_="District"),
        UGSubdivision(code="UG-224", name="Namutumba", type_="District"),
        UGSubdivision(code="UG-225", name="Bulambuli", type_="District"),
        UGSubdivision(code="UG-226", name="Buyende", type_="District"),
        UGSubdivision(code="UG-227", name="Kibuku", type_="District"),
        UGSubdivision(code="UG-228", name="Kween", type_="District"),
        UGSubdivision(code="UG-229", name="Luuka", type_="District"),
        UGSubdivision(code="UG-230", name="Namayingo", type_="District"),
        UGSubdivision(code="UG-231", name="Ngora", type_="District"),
        UGSubdivision(code="UG-232", name="Serere", type_="District"),
        UGSubdivision(code="UG-233", name="Butebo", type_="District"),
        UGSubdivision(code="UG-234", name="Namisindwa", type_="District"),
        UGSubdivision(code="UG-235", name="Bugweri", type_="District"),
        UGSubdivision(code="UG-236", name="Kapelebyong", type_="District"),
        UGSubdivision(code="UG-237", name="Kalaki", type_="District"),
        UGSubdivision(code="UG-301", name="Adjumani", type_="District"),
        UGSubdivision(code="UG-302", name="Apac", type_="District"),
        UGSubdivision(code="UG-303", name="Arua", type_="District"),
        UGSubdivision(code="UG-304", name="Gulu", type_="District"),
        UGSubdivision(code="UG-305", name="Kitgum", type_="District"),
        UGSubdivision(code="UG-306", name="Kotido", type_="District"),
        UGSubdivision(code="UG-307", name="Lira", type_="District"),
        UGSubdivision(code="UG-308", name="Moroto", type_="District"),
        UGSubdivision(code="UG-309", name="Moyo", type_="District"),
        UGSubdivision(code="UG-310", name="Nebbi", type_="District"),
        UGSubdivision(code="UG-311", name="Nakapiripirit", type_="District"),
        UGSubdivision(code="UG-312", name="Pader", type_="District"),
        UGSubdivision(code="UG-313", name="Yumbe", type_="District"),
        UGSubdivision(code="UG-314", name="Abim", type_="District"),
        UGSubdivision(code="UG-315", name="Amolatar", type_="District"),
        UGSubdivision(code="UG-316", name="Amuru", type_="District"),
        UGSubdivision(code="UG-317", name="Dokolo", type_="District"),
        UGSubdivision(code="UG-318", name="Kaabong", type_="District"),
        UGSubdivision(code="UG-319", name="Koboko", type_="District"),
        UGSubdivision(code="UG-320", name="Maracha", type_="District"),
        UGSubdivision(code="UG-321", name="Oyam", type_="District"),
        UGSubdivision(code="UG-322", name="Agago", type_="District"),
        UGSubdivision(code="UG-323", name="Alebtong", type_="District"),
        UGSubdivision(code="UG-324", name="Amudat", type_="District"),
        UGSubdivision(code="UG-325", name="Kole", type_="District"),
        UGSubdivision(code="UG-326", name="Lamwo", type_="District"),
        UGSubdivision(code="UG-327", name="Napak", type_="District"),
        UGSubdivision(code="UG-328", name="Nwoya", type_="District"),
        UGSubdivision(code="UG-329", name="Otuke", type_="District"),
        UGSubdivision(code="UG-330", name="Zombo", type_="District"),
        UGSubdivision(code="UG-331", name="Omoro", type_="District"),
        UGSubdivision(code="UG-332", name="Pakwach", type_="District"),
        UGSubdivision(code="UG-333", name="Kwania", type_="District"),
        UGSubdivision(code="UG-334", name="Nabilatuk", type_="District"),
        UGSubdivision(code="UG-335", name="Karenga", type_="District"),
        UGSubdivision(code="UG-336", name="Madi-Okollo", type_="District"),
        UGSubdivision(code="UG-337", name="Obongi", type_="District"),
        UGSubdivision(code="UG-401", name="Bundibugyo", type_="District"),
        UGSubdivision(code="UG-402", name="Bushenyi", type_="District"),
        UGSubdivision(code="UG-403", name="Hoima", type_="District"),
        UGSubdivision(code="UG-404", name="Kabale", type_="District"),
        UGSubdivision(code="UG-405", name="Kabarole", type_="District"),
        UGSubdivision(code="UG-406", name="Kasese", type_="District"),
        UGSubdivision(code="UG-407", name="Kibaale", type_="District"),
        UGSubdivision(code="UG-408", name="Kisoro", type_="District"),
        UGSubdivision(code="UG-409", name="Masindi", type_="District"),
        UGSubdivision(code="UG-410", name="Mbarara", type_="District"),
        UGSubdivision(code="UG-411", name="Ntungamo", type_="District"),
        UGSubdivision(code="UG-412", name="Rukungiri", type_="District"),
        UGSubdivision(code="UG-413", name="Kamwenge", type_="District"),
        UGSubdivision(code="UG-414", name="Kanungu", type_="District"),
        UGSubdivision(code="UG-415", name="Kyenjojo", type_="District"),
        UGSubdivision(code="UG-416", name="Buliisa", type_="District"),
        UGSubdivision(code="UG-417", name="Ibanda", type_="District"),
        UGSubdivision(code="UG-418", name="Isingiro", type_="District"),
        UGSubdivision(code="UG-419", name="Kiruhura", type_="District"),
        UGSubdivision(code="UG-420", name="Buhweju", type_="District"),
        UGSubdivision(code="UG-421", name="Kiryandongo", type_="District"),
        UGSubdivision(code="UG-422", name="Kyegegwa", type_="District"),
        UGSubdivision(code="UG-423", name="Mitooma", type_="District"),
        UGSubdivision(code="UG-424", name="Ntoroko", type_="District"),
        UGSubdivision(code="UG-425", name="Rubirizi", type_="District"),
        UGSubdivision(code="UG-426", name="Sheema", type_="District"),
        UGSubdivision(code="UG-427", name="Kagadi", type_="District"),
        UGSubdivision(code="UG-428", name="Kakumiro", type_="District"),
        UGSubdivision(code="UG-429", name="Rubanda", type_="District"),
        UGSubdivision(code="UG-430", name="Bunyangabu", type_="District"),
        UGSubdivision(code="UG-431", name="Rukiga", type_="District"),
        UGSubdivision(code="UG-432", name="Kikuube", type_="District"),
        UGSubdivision(code="UG-433", name="Kazo", type_="District"),
        UGSubdivision(code="UG-434", name="Kitagwenda", type_="District"),
        UGSubdivision(code="UG-435", name="Rwampara", type_="District"),
        UGSubdivision(code="UG-C", name="Central", type_="Geographical region"),
        UGSubdivision(code="UG-E", name="Eastern", type_="Geographical region"),
        UGSubdivision(code="UG-N", name="Northern", type_="Geographical region"),
        UGSubdivision(code="UG-W", name="Western", type_="Geographical region"),
    ],
)
