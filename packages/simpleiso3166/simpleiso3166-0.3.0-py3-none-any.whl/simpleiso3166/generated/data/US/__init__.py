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

USSubdivisionCodeType = Literal[
    "US-AK",  # Alaska
    "US-AL",  # Alabama
    "US-AR",  # Arkansas
    "US-AS",  # American Samoa
    "US-AZ",  # Arizona
    "US-CA",  # California
    "US-CO",  # Colorado
    "US-CT",  # Connecticut
    "US-DC",  # District of Columbia
    "US-DE",  # Delaware
    "US-FL",  # Florida
    "US-GA",  # Georgia
    "US-GU",  # Guam
    "US-HI",  # Hawaii
    "US-IA",  # Iowa
    "US-ID",  # Idaho
    "US-IL",  # Illinois
    "US-IN",  # Indiana
    "US-KS",  # Kansas
    "US-KY",  # Kentucky
    "US-LA",  # Louisiana
    "US-MA",  # Massachusetts
    "US-MD",  # Maryland
    "US-ME",  # Maine
    "US-MI",  # Michigan
    "US-MN",  # Minnesota
    "US-MO",  # Missouri
    "US-MP",  # Northern Mariana Islands
    "US-MS",  # Mississippi
    "US-MT",  # Montana
    "US-NC",  # North Carolina
    "US-ND",  # North Dakota
    "US-NE",  # Nebraska
    "US-NH",  # New Hampshire
    "US-NJ",  # New Jersey
    "US-NM",  # New Mexico
    "US-NV",  # Nevada
    "US-NY",  # New York
    "US-OH",  # Ohio
    "US-OK",  # Oklahoma
    "US-OR",  # Oregon
    "US-PA",  # Pennsylvania
    "US-PR",  # Puerto Rico
    "US-RI",  # Rhode Island
    "US-SC",  # South Carolina
    "US-SD",  # South Dakota
    "US-TN",  # Tennessee
    "US-TX",  # Texas
    "US-UM",  # United States Minor Outlying Islands
    "US-UT",  # Utah
    "US-VA",  # Virginia
    "US-VI",  # Virgin Islands, U.S.
    "US-VT",  # Vermont
    "US-WA",  # Washington
    "US-WI",  # Wisconsin
    "US-WV",  # West Virginia
    "US-WY",  # Wyoming
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class USSubdivision(Subdivision):
    code: USSubdivisionCodeType


US: Final[Country] = Country(
    alpha2="US",
    alpha3="USA",
    name="United States",
    common_name=None,
    official_name="United States of America",
    subdivisions=[
        USSubdivision(code="US-AK", name="Alaska", type_="State"),
        USSubdivision(code="US-AL", name="Alabama", type_="State"),
        USSubdivision(code="US-AR", name="Arkansas", type_="State"),
        USSubdivision(code="US-AS", name="American Samoa", type_="Outlying area"),
        USSubdivision(code="US-AZ", name="Arizona", type_="State"),
        USSubdivision(code="US-CA", name="California", type_="State"),
        USSubdivision(code="US-CO", name="Colorado", type_="State"),
        USSubdivision(code="US-CT", name="Connecticut", type_="State"),
        USSubdivision(code="US-DC", name="District of Columbia", type_="District"),
        USSubdivision(code="US-DE", name="Delaware", type_="State"),
        USSubdivision(code="US-FL", name="Florida", type_="State"),
        USSubdivision(code="US-GA", name="Georgia", type_="State"),
        USSubdivision(code="US-GU", name="Guam", type_="Outlying area"),
        USSubdivision(code="US-HI", name="Hawaii", type_="State"),
        USSubdivision(code="US-IA", name="Iowa", type_="State"),
        USSubdivision(code="US-ID", name="Idaho", type_="State"),
        USSubdivision(code="US-IL", name="Illinois", type_="State"),
        USSubdivision(code="US-IN", name="Indiana", type_="State"),
        USSubdivision(code="US-KS", name="Kansas", type_="State"),
        USSubdivision(code="US-KY", name="Kentucky", type_="State"),
        USSubdivision(code="US-LA", name="Louisiana", type_="State"),
        USSubdivision(code="US-MA", name="Massachusetts", type_="State"),
        USSubdivision(code="US-MD", name="Maryland", type_="State"),
        USSubdivision(code="US-ME", name="Maine", type_="State"),
        USSubdivision(code="US-MI", name="Michigan", type_="State"),
        USSubdivision(code="US-MN", name="Minnesota", type_="State"),
        USSubdivision(code="US-MO", name="Missouri", type_="State"),
        USSubdivision(code="US-MP", name="Northern Mariana Islands", type_="Outlying area"),
        USSubdivision(code="US-MS", name="Mississippi", type_="State"),
        USSubdivision(code="US-MT", name="Montana", type_="State"),
        USSubdivision(code="US-NC", name="North Carolina", type_="State"),
        USSubdivision(code="US-ND", name="North Dakota", type_="State"),
        USSubdivision(code="US-NE", name="Nebraska", type_="State"),
        USSubdivision(code="US-NH", name="New Hampshire", type_="State"),
        USSubdivision(code="US-NJ", name="New Jersey", type_="State"),
        USSubdivision(code="US-NM", name="New Mexico", type_="State"),
        USSubdivision(code="US-NV", name="Nevada", type_="State"),
        USSubdivision(code="US-NY", name="New York", type_="State"),
        USSubdivision(code="US-OH", name="Ohio", type_="State"),
        USSubdivision(code="US-OK", name="Oklahoma", type_="State"),
        USSubdivision(code="US-OR", name="Oregon", type_="State"),
        USSubdivision(code="US-PA", name="Pennsylvania", type_="State"),
        USSubdivision(code="US-PR", name="Puerto Rico", type_="Outlying area"),
        USSubdivision(code="US-RI", name="Rhode Island", type_="State"),
        USSubdivision(code="US-SC", name="South Carolina", type_="State"),
        USSubdivision(code="US-SD", name="South Dakota", type_="State"),
        USSubdivision(code="US-TN", name="Tennessee", type_="State"),
        USSubdivision(code="US-TX", name="Texas", type_="State"),
        USSubdivision(code="US-UM", name="United States Minor Outlying Islands", type_="Outlying area"),
        USSubdivision(code="US-UT", name="Utah", type_="State"),
        USSubdivision(code="US-VA", name="Virginia", type_="State"),
        USSubdivision(code="US-VI", name="Virgin Islands, U.S.", type_="Outlying area"),
        USSubdivision(code="US-VT", name="Vermont", type_="State"),
        USSubdivision(code="US-WA", name="Washington", type_="State"),
        USSubdivision(code="US-WI", name="Wisconsin", type_="State"),
        USSubdivision(code="US-WV", name="West Virginia", type_="State"),
        USSubdivision(code="US-WY", name="Wyoming", type_="State"),
    ],
)
