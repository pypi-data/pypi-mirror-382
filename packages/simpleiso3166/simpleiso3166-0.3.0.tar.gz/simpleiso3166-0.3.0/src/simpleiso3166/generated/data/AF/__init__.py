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

AFSubdivisionCodeType = Literal[
    "AF-BAL",  # Balkh
    "AF-BAM",  # Bāmyān
    "AF-BDG",  # Bādghīs
    "AF-BDS",  # Badakhshān
    "AF-BGL",  # Baghlān
    "AF-DAY",  # Dāykundī
    "AF-FRA",  # Farāh
    "AF-FYB",  # Fāryāb
    "AF-GHA",  # Ghaznī
    "AF-GHO",  # Ghōr
    "AF-HEL",  # Helmand
    "AF-HER",  # Herāt
    "AF-JOW",  # Jowzjān
    "AF-KAB",  # Kābul
    "AF-KAN",  # Kandahār
    "AF-KAP",  # Kāpīsā
    "AF-KDZ",  # Kunduz
    "AF-KHO",  # Khōst
    "AF-KNR",  # Kunaṟ
    "AF-LAG",  # Laghmān
    "AF-LOG",  # Lōgar
    "AF-NAN",  # Nangarhār
    "AF-NIM",  # Nīmrōz
    "AF-NUR",  # Nūristān
    "AF-PAN",  # Panjshayr
    "AF-PAR",  # Parwān
    "AF-PIA",  # Paktiyā
    "AF-PKA",  # Paktīkā
    "AF-SAM",  # Samangān
    "AF-SAR",  # Sar-e Pul
    "AF-TAK",  # Takhār
    "AF-URU",  # Uruzgān
    "AF-WAR",  # Wardak
    "AF-ZAB",  # Zābul
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class AFSubdivision(Subdivision):
    code: AFSubdivisionCodeType


AF: Final[Country] = Country(
    alpha2="AF",
    alpha3="AFG",
    name="Afghanistan",
    common_name=None,
    official_name="Islamic Republic of Afghanistan",
    subdivisions=[
        AFSubdivision(code="AF-BAL", name="Balkh", type_="Province"),
        AFSubdivision(code="AF-BAM", name="Bāmyān", type_="Province"),
        AFSubdivision(code="AF-BDG", name="Bādghīs", type_="Province"),
        AFSubdivision(code="AF-BDS", name="Badakhshān", type_="Province"),
        AFSubdivision(code="AF-BGL", name="Baghlān", type_="Province"),
        AFSubdivision(code="AF-DAY", name="Dāykundī", type_="Province"),
        AFSubdivision(code="AF-FRA", name="Farāh", type_="Province"),
        AFSubdivision(code="AF-FYB", name="Fāryāb", type_="Province"),
        AFSubdivision(code="AF-GHA", name="Ghaznī", type_="Province"),
        AFSubdivision(code="AF-GHO", name="Ghōr", type_="Province"),
        AFSubdivision(code="AF-HEL", name="Helmand", type_="Province"),
        AFSubdivision(code="AF-HER", name="Herāt", type_="Province"),
        AFSubdivision(code="AF-JOW", name="Jowzjān", type_="Province"),
        AFSubdivision(code="AF-KAB", name="Kābul", type_="Province"),
        AFSubdivision(code="AF-KAN", name="Kandahār", type_="Province"),
        AFSubdivision(code="AF-KAP", name="Kāpīsā", type_="Province"),
        AFSubdivision(code="AF-KDZ", name="Kunduz", type_="Province"),
        AFSubdivision(code="AF-KHO", name="Khōst", type_="Province"),
        AFSubdivision(code="AF-KNR", name="Kunaṟ", type_="Province"),
        AFSubdivision(code="AF-LAG", name="Laghmān", type_="Province"),
        AFSubdivision(code="AF-LOG", name="Lōgar", type_="Province"),
        AFSubdivision(code="AF-NAN", name="Nangarhār", type_="Province"),
        AFSubdivision(code="AF-NIM", name="Nīmrōz", type_="Province"),
        AFSubdivision(code="AF-NUR", name="Nūristān", type_="Province"),
        AFSubdivision(code="AF-PAN", name="Panjshayr", type_="Province"),
        AFSubdivision(code="AF-PAR", name="Parwān", type_="Province"),
        AFSubdivision(code="AF-PIA", name="Paktiyā", type_="Province"),
        AFSubdivision(code="AF-PKA", name="Paktīkā", type_="Province"),
        AFSubdivision(code="AF-SAM", name="Samangān", type_="Province"),
        AFSubdivision(code="AF-SAR", name="Sar-e Pul", type_="Province"),
        AFSubdivision(code="AF-TAK", name="Takhār", type_="Province"),
        AFSubdivision(code="AF-URU", name="Uruzgān", type_="Province"),
        AFSubdivision(code="AF-WAR", name="Wardak", type_="Province"),
        AFSubdivision(code="AF-ZAB", name="Zābul", type_="Province"),
    ],
)
