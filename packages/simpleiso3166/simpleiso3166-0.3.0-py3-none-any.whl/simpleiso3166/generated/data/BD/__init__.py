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

BDSubdivisionCodeType = Literal[
    "BD-01",  # Bandarban
    "BD-02",  # Barguna
    "BD-03",  # Bogura
    "BD-04",  # Brahmanbaria
    "BD-05",  # Bagerhat
    "BD-06",  # Barishal
    "BD-07",  # Bhola
    "BD-08",  # Cumilla
    "BD-09",  # Chandpur
    "BD-10",  # Chattogram
    "BD-11",  # Cox's Bazar
    "BD-12",  # Chuadanga
    "BD-13",  # Dhaka
    "BD-14",  # Dinajpur
    "BD-15",  # Faridpur
    "BD-16",  # Feni
    "BD-17",  # Gopalganj
    "BD-18",  # Gazipur
    "BD-19",  # Gaibandha
    "BD-20",  # Habiganj
    "BD-21",  # Jamalpur
    "BD-22",  # Jashore
    "BD-23",  # Jhenaidah
    "BD-24",  # Joypurhat
    "BD-25",  # Jhalakathi
    "BD-26",  # Kishoreganj
    "BD-27",  # Khulna
    "BD-28",  # Kurigram
    "BD-29",  # Khagrachhari
    "BD-30",  # Kushtia
    "BD-31",  # Lakshmipur
    "BD-32",  # Lalmonirhat
    "BD-33",  # Manikganj
    "BD-34",  # Mymensingh
    "BD-35",  # Munshiganj
    "BD-36",  # Madaripur
    "BD-37",  # Magura
    "BD-38",  # Moulvibazar
    "BD-39",  # Meherpur
    "BD-40",  # Narayanganj
    "BD-41",  # Netrakona
    "BD-42",  # Narsingdi
    "BD-43",  # Narail
    "BD-44",  # Natore
    "BD-45",  # Chapai Nawabganj
    "BD-46",  # Nilphamari
    "BD-47",  # Noakhali
    "BD-48",  # Naogaon
    "BD-49",  # Pabna
    "BD-50",  # Pirojpur
    "BD-51",  # Patuakhali
    "BD-52",  # Panchagarh
    "BD-53",  # Rajbari
    "BD-54",  # Rajshahi
    "BD-55",  # Rangpur
    "BD-56",  # Rangamati
    "BD-57",  # Sherpur
    "BD-58",  # Satkhira
    "BD-59",  # Sirajganj
    "BD-60",  # Sylhet
    "BD-61",  # Sunamganj
    "BD-62",  # Shariatpur
    "BD-63",  # Tangail
    "BD-64",  # Thakurgaon
    "BD-A",  # Barishal
    "BD-B",  # Chattogram
    "BD-C",  # Dhaka
    "BD-D",  # Khulna
    "BD-E",  # Rajshahi
    "BD-F",  # Rangpur
    "BD-G",  # Sylhet
    "BD-H",  # Mymensingh
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class BDSubdivision(Subdivision):
    code: BDSubdivisionCodeType


BD: Final[Country] = Country(
    alpha2="BD",
    alpha3="BGD",
    name="Bangladesh",
    common_name=None,
    official_name="People's Republic of Bangladesh",
    subdivisions=[
        BDSubdivision(code="BD-01", name="Bandarban", type_="District"),
        BDSubdivision(code="BD-02", name="Barguna", type_="District"),
        BDSubdivision(code="BD-03", name="Bogura", type_="District"),
        BDSubdivision(code="BD-04", name="Brahmanbaria", type_="District"),
        BDSubdivision(code="BD-05", name="Bagerhat", type_="District"),
        BDSubdivision(code="BD-06", name="Barishal", type_="District"),
        BDSubdivision(code="BD-07", name="Bhola", type_="District"),
        BDSubdivision(code="BD-08", name="Cumilla", type_="District"),
        BDSubdivision(code="BD-09", name="Chandpur", type_="District"),
        BDSubdivision(code="BD-10", name="Chattogram", type_="District"),
        BDSubdivision(code="BD-11", name="Cox's Bazar", type_="District"),
        BDSubdivision(code="BD-12", name="Chuadanga", type_="District"),
        BDSubdivision(code="BD-13", name="Dhaka", type_="District"),
        BDSubdivision(code="BD-14", name="Dinajpur", type_="District"),
        BDSubdivision(code="BD-15", name="Faridpur", type_="District"),
        BDSubdivision(code="BD-16", name="Feni", type_="District"),
        BDSubdivision(code="BD-17", name="Gopalganj", type_="District"),
        BDSubdivision(code="BD-18", name="Gazipur", type_="District"),
        BDSubdivision(code="BD-19", name="Gaibandha", type_="District"),
        BDSubdivision(code="BD-20", name="Habiganj", type_="District"),
        BDSubdivision(code="BD-21", name="Jamalpur", type_="District"),
        BDSubdivision(code="BD-22", name="Jashore", type_="District"),
        BDSubdivision(code="BD-23", name="Jhenaidah", type_="District"),
        BDSubdivision(code="BD-24", name="Joypurhat", type_="District"),
        BDSubdivision(code="BD-25", name="Jhalakathi", type_="District"),
        BDSubdivision(code="BD-26", name="Kishoreganj", type_="District"),
        BDSubdivision(code="BD-27", name="Khulna", type_="District"),
        BDSubdivision(code="BD-28", name="Kurigram", type_="District"),
        BDSubdivision(code="BD-29", name="Khagrachhari", type_="District"),
        BDSubdivision(code="BD-30", name="Kushtia", type_="District"),
        BDSubdivision(code="BD-31", name="Lakshmipur", type_="District"),
        BDSubdivision(code="BD-32", name="Lalmonirhat", type_="District"),
        BDSubdivision(code="BD-33", name="Manikganj", type_="District"),
        BDSubdivision(code="BD-34", name="Mymensingh", type_="District"),
        BDSubdivision(code="BD-35", name="Munshiganj", type_="District"),
        BDSubdivision(code="BD-36", name="Madaripur", type_="District"),
        BDSubdivision(code="BD-37", name="Magura", type_="District"),
        BDSubdivision(code="BD-38", name="Moulvibazar", type_="District"),
        BDSubdivision(code="BD-39", name="Meherpur", type_="District"),
        BDSubdivision(code="BD-40", name="Narayanganj", type_="District"),
        BDSubdivision(code="BD-41", name="Netrakona", type_="District"),
        BDSubdivision(code="BD-42", name="Narsingdi", type_="District"),
        BDSubdivision(code="BD-43", name="Narail", type_="District"),
        BDSubdivision(code="BD-44", name="Natore", type_="District"),
        BDSubdivision(code="BD-45", name="Chapai Nawabganj", type_="District"),
        BDSubdivision(code="BD-46", name="Nilphamari", type_="District"),
        BDSubdivision(code="BD-47", name="Noakhali", type_="District"),
        BDSubdivision(code="BD-48", name="Naogaon", type_="District"),
        BDSubdivision(code="BD-49", name="Pabna", type_="District"),
        BDSubdivision(code="BD-50", name="Pirojpur", type_="District"),
        BDSubdivision(code="BD-51", name="Patuakhali", type_="District"),
        BDSubdivision(code="BD-52", name="Panchagarh", type_="District"),
        BDSubdivision(code="BD-53", name="Rajbari", type_="District"),
        BDSubdivision(code="BD-54", name="Rajshahi", type_="District"),
        BDSubdivision(code="BD-55", name="Rangpur", type_="District"),
        BDSubdivision(code="BD-56", name="Rangamati", type_="District"),
        BDSubdivision(code="BD-57", name="Sherpur", type_="District"),
        BDSubdivision(code="BD-58", name="Satkhira", type_="District"),
        BDSubdivision(code="BD-59", name="Sirajganj", type_="District"),
        BDSubdivision(code="BD-60", name="Sylhet", type_="District"),
        BDSubdivision(code="BD-61", name="Sunamganj", type_="District"),
        BDSubdivision(code="BD-62", name="Shariatpur", type_="District"),
        BDSubdivision(code="BD-63", name="Tangail", type_="District"),
        BDSubdivision(code="BD-64", name="Thakurgaon", type_="District"),
        BDSubdivision(code="BD-A", name="Barishal", type_="Division"),
        BDSubdivision(code="BD-B", name="Chattogram", type_="Division"),
        BDSubdivision(code="BD-C", name="Dhaka", type_="Division"),
        BDSubdivision(code="BD-D", name="Khulna", type_="Division"),
        BDSubdivision(code="BD-E", name="Rajshahi", type_="Division"),
        BDSubdivision(code="BD-F", name="Rangpur", type_="Division"),
        BDSubdivision(code="BD-G", name="Sylhet", type_="Division"),
        BDSubdivision(code="BD-H", name="Mymensingh", type_="Division"),
    ],
)
