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

RSSubdivisionCodeType = Literal[
    "RS-00",  # Beograd
    "RS-01",  # Severnobački okrug
    "RS-02",  # Srednjebanatski okrug
    "RS-03",  # Severnobanatski okrug
    "RS-04",  # Južnobanatski okrug
    "RS-05",  # Zapadnobački okrug
    "RS-06",  # Južnobački okrug
    "RS-07",  # Sremski okrug
    "RS-08",  # Mačvanski okrug
    "RS-09",  # Kolubarski okrug
    "RS-10",  # Podunavski okrug
    "RS-11",  # Braničevski okrug
    "RS-12",  # Šumadijski okrug
    "RS-13",  # Pomoravski okrug
    "RS-14",  # Borski okrug
    "RS-15",  # Zaječarski okrug
    "RS-16",  # Zlatiborski okrug
    "RS-17",  # Moravički okrug
    "RS-18",  # Raški okrug
    "RS-19",  # Rasinski okrug
    "RS-20",  # Nišavski okrug
    "RS-21",  # Toplički okrug
    "RS-22",  # Pirotski okrug
    "RS-23",  # Jablanički okrug
    "RS-24",  # Pčinjski okrug
    "RS-25",  # Kosovski okrug
    "RS-26",  # Pećki okrug
    "RS-27",  # Prizrenski okrug
    "RS-28",  # Kosovsko-Mitrovački okrug
    "RS-29",  # Kosovsko-Pomoravski okrug
    "RS-KM",  # Kosovo-Metohija
    "RS-VO",  # Vojvodina
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class RSSubdivision(Subdivision):
    code: RSSubdivisionCodeType


RS: Final[Country] = Country(
    alpha2="RS",
    alpha3="SRB",
    name="Serbia",
    common_name=None,
    official_name="Republic of Serbia",
    subdivisions=[
        RSSubdivision(code="RS-00", name="Beograd", type_="City"),
        RSSubdivision(code="RS-01", name="Severnobački okrug", type_="District"),
        RSSubdivision(code="RS-02", name="Srednjebanatski okrug", type_="District"),
        RSSubdivision(code="RS-03", name="Severnobanatski okrug", type_="District"),
        RSSubdivision(code="RS-04", name="Južnobanatski okrug", type_="District"),
        RSSubdivision(code="RS-05", name="Zapadnobački okrug", type_="District"),
        RSSubdivision(code="RS-06", name="Južnobački okrug", type_="District"),
        RSSubdivision(code="RS-07", name="Sremski okrug", type_="District"),
        RSSubdivision(code="RS-08", name="Mačvanski okrug", type_="District"),
        RSSubdivision(code="RS-09", name="Kolubarski okrug", type_="District"),
        RSSubdivision(code="RS-10", name="Podunavski okrug", type_="District"),
        RSSubdivision(code="RS-11", name="Braničevski okrug", type_="District"),
        RSSubdivision(code="RS-12", name="Šumadijski okrug", type_="District"),
        RSSubdivision(code="RS-13", name="Pomoravski okrug", type_="District"),
        RSSubdivision(code="RS-14", name="Borski okrug", type_="District"),
        RSSubdivision(code="RS-15", name="Zaječarski okrug", type_="District"),
        RSSubdivision(code="RS-16", name="Zlatiborski okrug", type_="District"),
        RSSubdivision(code="RS-17", name="Moravički okrug", type_="District"),
        RSSubdivision(code="RS-18", name="Raški okrug", type_="District"),
        RSSubdivision(code="RS-19", name="Rasinski okrug", type_="District"),
        RSSubdivision(code="RS-20", name="Nišavski okrug", type_="District"),
        RSSubdivision(code="RS-21", name="Toplički okrug", type_="District"),
        RSSubdivision(code="RS-22", name="Pirotski okrug", type_="District"),
        RSSubdivision(code="RS-23", name="Jablanički okrug", type_="District"),
        RSSubdivision(code="RS-24", name="Pčinjski okrug", type_="District"),
        RSSubdivision(code="RS-25", name="Kosovski okrug", type_="District"),
        RSSubdivision(code="RS-26", name="Pećki okrug", type_="District"),
        RSSubdivision(code="RS-27", name="Prizrenski okrug", type_="District"),
        RSSubdivision(code="RS-28", name="Kosovsko-Mitrovački okrug", type_="District"),
        RSSubdivision(code="RS-29", name="Kosovsko-Pomoravski okrug", type_="District"),
        RSSubdivision(code="RS-KM", name="Kosovo-Metohija", type_="Autonomous province"),
        RSSubdivision(code="RS-VO", name="Vojvodina", type_="Autonomous province"),
    ],
)
