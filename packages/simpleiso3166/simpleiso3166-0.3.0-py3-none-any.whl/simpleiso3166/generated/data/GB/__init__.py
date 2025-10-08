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

GBSubdivisionCodeType = Literal[
    "GB-ABC",  # Armagh City, Banbridge and Craigavon
    "GB-ABD",  # Aberdeenshire
    "GB-ABE",  # Aberdeen City
    "GB-AGB",  # Argyll and Bute
    "GB-AGY",  # Isle of Anglesey [Sir Ynys Môn GB-YNM]
    "GB-AND",  # Ards and North Down
    "GB-ANN",  # Antrim and Newtownabbey
    "GB-ANS",  # Angus
    "GB-BAS",  # Bath and North East Somerset
    "GB-BBD",  # Blackburn with Darwen
    "GB-BCP",  # Bournemouth, Christchurch and Poole
    "GB-BDF",  # Bedford
    "GB-BDG",  # Barking and Dagenham
    "GB-BEN",  # Brent
    "GB-BEX",  # Bexley
    "GB-BFS",  # Belfast City
    "GB-BGE",  # Bridgend [Pen-y-bont ar Ogwr GB-POG]
    "GB-BGW",  # Blaenau Gwent
    "GB-BIR",  # Birmingham
    "GB-BKM",  # Buckinghamshire
    "GB-BNE",  # Barnet
    "GB-BNH",  # Brighton and Hove
    "GB-BNS",  # Barnsley
    "GB-BOL",  # Bolton
    "GB-BPL",  # Blackpool
    "GB-BRC",  # Bracknell Forest
    "GB-BRD",  # Bradford
    "GB-BRY",  # Bromley
    "GB-BST",  # Bristol, City of
    "GB-BUR",  # Bury
    "GB-CAM",  # Cambridgeshire
    "GB-CAY",  # Caerphilly [Caerffili GB-CAF]
    "GB-CBF",  # Central Bedfordshire
    "GB-CCG",  # Causeway Coast and Glens
    "GB-CGN",  # Ceredigion [Sir Ceredigion]
    "GB-CHE",  # Cheshire East
    "GB-CHW",  # Cheshire West and Chester
    "GB-CLD",  # Calderdale
    "GB-CLK",  # Clackmannanshire
    "GB-CMA",  # Cumbria
    "GB-CMD",  # Camden
    "GB-CMN",  # Carmarthenshire [Sir Gaerfyrddin GB-GFY]
    "GB-CON",  # Cornwall
    "GB-COV",  # Coventry
    "GB-CRF",  # Cardiff [Caerdydd GB-CRD]
    "GB-CRY",  # Croydon
    "GB-CWY",  # Conwy
    "GB-DAL",  # Darlington
    "GB-DBY",  # Derbyshire
    "GB-DEN",  # Denbighshire [Sir Ddinbych GB-DDB]
    "GB-DER",  # Derby
    "GB-DEV",  # Devon
    "GB-DGY",  # Dumfries and Galloway
    "GB-DNC",  # Doncaster
    "GB-DND",  # Dundee City
    "GB-DOR",  # Dorset
    "GB-DRS",  # Derry and Strabane
    "GB-DUD",  # Dudley
    "GB-DUR",  # Durham, County
    "GB-EAL",  # Ealing
    "GB-EAY",  # East Ayrshire
    "GB-EDH",  # Edinburgh, City of
    "GB-EDU",  # East Dunbartonshire
    "GB-ELN",  # East Lothian
    "GB-ELS",  # Eilean Siar
    "GB-ENF",  # Enfield
    "GB-ENG",  # England
    "GB-ERW",  # East Renfrewshire
    "GB-ERY",  # East Riding of Yorkshire
    "GB-ESS",  # Essex
    "GB-ESX",  # East Sussex
    "GB-FAL",  # Falkirk
    "GB-FIF",  # Fife
    "GB-FLN",  # Flintshire [Sir y Fflint GB-FFL]
    "GB-FMO",  # Fermanagh and Omagh
    "GB-GAT",  # Gateshead
    "GB-GLG",  # Glasgow City
    "GB-GLS",  # Gloucestershire
    "GB-GRE",  # Greenwich
    "GB-GWN",  # Gwynedd
    "GB-HAL",  # Halton
    "GB-HAM",  # Hampshire
    "GB-HAV",  # Havering
    "GB-HCK",  # Hackney
    "GB-HEF",  # Herefordshire
    "GB-HIL",  # Hillingdon
    "GB-HLD",  # Highland
    "GB-HMF",  # Hammersmith and Fulham
    "GB-HNS",  # Hounslow
    "GB-HPL",  # Hartlepool
    "GB-HRT",  # Hertfordshire
    "GB-HRW",  # Harrow
    "GB-HRY",  # Haringey
    "GB-IOS",  # Isles of Scilly
    "GB-IOW",  # Isle of Wight
    "GB-ISL",  # Islington
    "GB-IVC",  # Inverclyde
    "GB-KEC",  # Kensington and Chelsea
    "GB-KEN",  # Kent
    "GB-KHL",  # Kingston upon Hull
    "GB-KIR",  # Kirklees
    "GB-KTT",  # Kingston upon Thames
    "GB-KWL",  # Knowsley
    "GB-LAN",  # Lancashire
    "GB-LBC",  # Lisburn and Castlereagh
    "GB-LBH",  # Lambeth
    "GB-LCE",  # Leicester
    "GB-LDS",  # Leeds
    "GB-LEC",  # Leicestershire
    "GB-LEW",  # Lewisham
    "GB-LIN",  # Lincolnshire
    "GB-LIV",  # Liverpool
    "GB-LND",  # London, City of
    "GB-LUT",  # Luton
    "GB-MAN",  # Manchester
    "GB-MDB",  # Middlesbrough
    "GB-MDW",  # Medway
    "GB-MEA",  # Mid and East Antrim
    "GB-MIK",  # Milton Keynes
    "GB-MLN",  # Midlothian
    "GB-MON",  # Monmouthshire [Sir Fynwy GB-FYN]
    "GB-MRT",  # Merton
    "GB-MRY",  # Moray
    "GB-MTY",  # Merthyr Tydfil [Merthyr Tudful GB-MTU]
    "GB-MUL",  # Mid-Ulster
    "GB-NAY",  # North Ayrshire
    "GB-NBL",  # Northumberland
    "GB-NEL",  # North East Lincolnshire
    "GB-NET",  # Newcastle upon Tyne
    "GB-NFK",  # Norfolk
    "GB-NGM",  # Nottingham
    "GB-NIR",  # Northern Ireland
    "GB-NLK",  # North Lanarkshire
    "GB-NLN",  # North Lincolnshire
    "GB-NMD",  # Newry, Mourne and Down
    "GB-NNH",  # North Northamptonshire
    "GB-NSM",  # North Somerset
    "GB-NTL",  # Neath Port Talbot [Castell-nedd Port Talbot GB-CTL]
    "GB-NTT",  # Nottinghamshire
    "GB-NTY",  # North Tyneside
    "GB-NWM",  # Newham
    "GB-NWP",  # Newport [Casnewydd GB-CNW]
    "GB-NYK",  # North Yorkshire
    "GB-OLD",  # Oldham
    "GB-ORK",  # Orkney Islands
    "GB-OXF",  # Oxfordshire
    "GB-PEM",  # Pembrokeshire [Sir Benfro GB-BNF]
    "GB-PKN",  # Perth and Kinross
    "GB-PLY",  # Plymouth
    "GB-POR",  # Portsmouth
    "GB-POW",  # Powys
    "GB-PTE",  # Peterborough
    "GB-RCC",  # Redcar and Cleveland
    "GB-RCH",  # Rochdale
    "GB-RCT",  # Rhondda Cynon Taff [Rhondda CynonTaf]
    "GB-RDB",  # Redbridge
    "GB-RDG",  # Reading
    "GB-RFW",  # Renfrewshire
    "GB-RIC",  # Richmond upon Thames
    "GB-ROT",  # Rotherham
    "GB-RUT",  # Rutland
    "GB-SAW",  # Sandwell
    "GB-SAY",  # South Ayrshire
    "GB-SCB",  # Scottish Borders
    "GB-SCT",  # Scotland
    "GB-SFK",  # Suffolk
    "GB-SFT",  # Sefton
    "GB-SGC",  # South Gloucestershire
    "GB-SHF",  # Sheffield
    "GB-SHN",  # St. Helens
    "GB-SHR",  # Shropshire
    "GB-SKP",  # Stockport
    "GB-SLF",  # Salford
    "GB-SLG",  # Slough
    "GB-SLK",  # South Lanarkshire
    "GB-SND",  # Sunderland
    "GB-SOL",  # Solihull
    "GB-SOM",  # Somerset
    "GB-SOS",  # Southend-on-Sea
    "GB-SRY",  # Surrey
    "GB-STE",  # Stoke-on-Trent
    "GB-STG",  # Stirling
    "GB-STH",  # Southampton
    "GB-STN",  # Sutton
    "GB-STS",  # Staffordshire
    "GB-STT",  # Stockton-on-Tees
    "GB-STY",  # South Tyneside
    "GB-SWA",  # Swansea [Abertawe GB-ATA]
    "GB-SWD",  # Swindon
    "GB-SWK",  # Southwark
    "GB-TAM",  # Tameside
    "GB-TFW",  # Telford and Wrekin
    "GB-THR",  # Thurrock
    "GB-TOB",  # Torbay
    "GB-TOF",  # Torfaen [Tor-faen]
    "GB-TRF",  # Trafford
    "GB-TWH",  # Tower Hamlets
    "GB-VGL",  # Vale of Glamorgan, The [Bro Morgannwg GB-BMG]
    "GB-WAR",  # Warwickshire
    "GB-WBK",  # West Berkshire
    "GB-WDU",  # West Dunbartonshire
    "GB-WFT",  # Waltham Forest
    "GB-WGN",  # Wigan
    "GB-WIL",  # Wiltshire
    "GB-WKF",  # Wakefield
    "GB-WLL",  # Walsall
    "GB-WLN",  # West Lothian
    "GB-WLS",  # Wales [Cymru GB-CYM]
    "GB-WLV",  # Wolverhampton
    "GB-WND",  # Wandsworth
    "GB-WNH",  # West Northamptonshire
    "GB-WNM",  # Windsor and Maidenhead
    "GB-WOK",  # Wokingham
    "GB-WOR",  # Worcestershire
    "GB-WRL",  # Wirral
    "GB-WRT",  # Warrington
    "GB-WRX",  # Wrexham [Wrecsam GB-WRC]
    "GB-WSM",  # Westminster
    "GB-WSX",  # West Sussex
    "GB-YOR",  # York
    "GB-ZET",  # Shetland Islands
]


@dataclasses.dataclass(**DATACLASS_BASE_AGS)
class GBSubdivision(Subdivision):
    code: GBSubdivisionCodeType


GB: Final[Country] = Country(
    alpha2="GB",
    alpha3="GBR",
    name="United Kingdom",
    common_name=None,
    official_name="United Kingdom of Great Britain and Northern Ireland",
    subdivisions=[
        GBSubdivision(code="GB-ABC", name="Armagh City, Banbridge and Craigavon", type_="District"),
        GBSubdivision(code="GB-ABD", name="Aberdeenshire", type_="Council area"),
        GBSubdivision(code="GB-ABE", name="Aberdeen City", type_="Council area"),
        GBSubdivision(code="GB-AGB", name="Argyll and Bute", type_="Council area"),
        GBSubdivision(code="GB-AGY", name="Isle of Anglesey [Sir Ynys Môn GB-YNM]", type_="Unitary authority"),
        GBSubdivision(code="GB-AND", name="Ards and North Down", type_="District"),
        GBSubdivision(code="GB-ANN", name="Antrim and Newtownabbey", type_="District"),
        GBSubdivision(code="GB-ANS", name="Angus", type_="Council area"),
        GBSubdivision(code="GB-BAS", name="Bath and North East Somerset", type_="Unitary authority"),
        GBSubdivision(code="GB-BBD", name="Blackburn with Darwen", type_="Unitary authority"),
        GBSubdivision(code="GB-BCP", name="Bournemouth, Christchurch and Poole", type_="Unitary authority"),
        GBSubdivision(code="GB-BDF", name="Bedford", type_="Unitary authority"),
        GBSubdivision(code="GB-BDG", name="Barking and Dagenham", type_="London borough"),
        GBSubdivision(code="GB-BEN", name="Brent", type_="London borough"),
        GBSubdivision(code="GB-BEX", name="Bexley", type_="London borough"),
        GBSubdivision(code="GB-BFS", name="Belfast City", type_="District"),
        GBSubdivision(code="GB-BGE", name="Bridgend [Pen-y-bont ar Ogwr GB-POG]", type_="Unitary authority"),
        GBSubdivision(code="GB-BGW", name="Blaenau Gwent", type_="Unitary authority"),
        GBSubdivision(code="GB-BIR", name="Birmingham", type_="Metropolitan district"),
        GBSubdivision(code="GB-BKM", name="Buckinghamshire", type_="Unitary authority"),
        GBSubdivision(code="GB-BNE", name="Barnet", type_="London borough"),
        GBSubdivision(code="GB-BNH", name="Brighton and Hove", type_="Unitary authority"),
        GBSubdivision(code="GB-BNS", name="Barnsley", type_="Metropolitan district"),
        GBSubdivision(code="GB-BOL", name="Bolton", type_="Metropolitan district"),
        GBSubdivision(code="GB-BPL", name="Blackpool", type_="Unitary authority"),
        GBSubdivision(code="GB-BRC", name="Bracknell Forest", type_="Unitary authority"),
        GBSubdivision(code="GB-BRD", name="Bradford", type_="Metropolitan district"),
        GBSubdivision(code="GB-BRY", name="Bromley", type_="London borough"),
        GBSubdivision(code="GB-BST", name="Bristol, City of", type_="Unitary authority"),
        GBSubdivision(code="GB-BUR", name="Bury", type_="Metropolitan district"),
        GBSubdivision(code="GB-CAM", name="Cambridgeshire", type_="Two-tier county"),
        GBSubdivision(code="GB-CAY", name="Caerphilly [Caerffili GB-CAF]", type_="Unitary authority"),
        GBSubdivision(code="GB-CBF", name="Central Bedfordshire", type_="Unitary authority"),
        GBSubdivision(code="GB-CCG", name="Causeway Coast and Glens", type_="District"),
        GBSubdivision(code="GB-CGN", name="Ceredigion [Sir Ceredigion]", type_="Unitary authority"),
        GBSubdivision(code="GB-CHE", name="Cheshire East", type_="Unitary authority"),
        GBSubdivision(code="GB-CHW", name="Cheshire West and Chester", type_="Unitary authority"),
        GBSubdivision(code="GB-CLD", name="Calderdale", type_="Metropolitan district"),
        GBSubdivision(code="GB-CLK", name="Clackmannanshire", type_="Council area"),
        GBSubdivision(code="GB-CMA", name="Cumbria", type_="Two-tier county"),
        GBSubdivision(code="GB-CMD", name="Camden", type_="London borough"),
        GBSubdivision(code="GB-CMN", name="Carmarthenshire [Sir Gaerfyrddin GB-GFY]", type_="Unitary authority"),
        GBSubdivision(code="GB-CON", name="Cornwall", type_="Unitary authority"),
        GBSubdivision(code="GB-COV", name="Coventry", type_="Metropolitan district"),
        GBSubdivision(code="GB-CRF", name="Cardiff [Caerdydd GB-CRD]", type_="Unitary authority"),
        GBSubdivision(code="GB-CRY", name="Croydon", type_="London borough"),
        GBSubdivision(code="GB-CWY", name="Conwy", type_="Unitary authority"),
        GBSubdivision(code="GB-DAL", name="Darlington", type_="Unitary authority"),
        GBSubdivision(code="GB-DBY", name="Derbyshire", type_="Two-tier county"),
        GBSubdivision(code="GB-DEN", name="Denbighshire [Sir Ddinbych GB-DDB]", type_="Unitary authority"),
        GBSubdivision(code="GB-DER", name="Derby", type_="Unitary authority"),
        GBSubdivision(code="GB-DEV", name="Devon", type_="Two-tier county"),
        GBSubdivision(code="GB-DGY", name="Dumfries and Galloway", type_="Council area"),
        GBSubdivision(code="GB-DNC", name="Doncaster", type_="Metropolitan district"),
        GBSubdivision(code="GB-DND", name="Dundee City", type_="Council area"),
        GBSubdivision(code="GB-DOR", name="Dorset", type_="Two-tier county"),
        GBSubdivision(code="GB-DRS", name="Derry and Strabane", type_="District"),
        GBSubdivision(code="GB-DUD", name="Dudley", type_="Metropolitan district"),
        GBSubdivision(code="GB-DUR", name="Durham, County", type_="Unitary authority"),
        GBSubdivision(code="GB-EAL", name="Ealing", type_="London borough"),
        GBSubdivision(code="GB-EAY", name="East Ayrshire", type_="Council area"),
        GBSubdivision(code="GB-EDH", name="Edinburgh, City of", type_="Council area"),
        GBSubdivision(code="GB-EDU", name="East Dunbartonshire", type_="Council area"),
        GBSubdivision(code="GB-ELN", name="East Lothian", type_="Council area"),
        GBSubdivision(code="GB-ELS", name="Eilean Siar", type_="Council area"),
        GBSubdivision(code="GB-ENF", name="Enfield", type_="London borough"),
        GBSubdivision(code="GB-ENG", name="England", type_="Country"),
        GBSubdivision(code="GB-ERW", name="East Renfrewshire", type_="Council area"),
        GBSubdivision(code="GB-ERY", name="East Riding of Yorkshire", type_="Unitary authority"),
        GBSubdivision(code="GB-ESS", name="Essex", type_="Two-tier county"),
        GBSubdivision(code="GB-ESX", name="East Sussex", type_="Two-tier county"),
        GBSubdivision(code="GB-FAL", name="Falkirk", type_="Council area"),
        GBSubdivision(code="GB-FIF", name="Fife", type_="Council area"),
        GBSubdivision(code="GB-FLN", name="Flintshire [Sir y Fflint GB-FFL]", type_="Unitary authority"),
        GBSubdivision(code="GB-FMO", name="Fermanagh and Omagh", type_="District"),
        GBSubdivision(code="GB-GAT", name="Gateshead", type_="Metropolitan district"),
        GBSubdivision(code="GB-GLG", name="Glasgow City", type_="Council area"),
        GBSubdivision(code="GB-GLS", name="Gloucestershire", type_="Two-tier county"),
        GBSubdivision(code="GB-GRE", name="Greenwich", type_="London borough"),
        GBSubdivision(code="GB-GWN", name="Gwynedd", type_="Unitary authority"),
        GBSubdivision(code="GB-HAL", name="Halton", type_="Unitary authority"),
        GBSubdivision(code="GB-HAM", name="Hampshire", type_="Two-tier county"),
        GBSubdivision(code="GB-HAV", name="Havering", type_="London borough"),
        GBSubdivision(code="GB-HCK", name="Hackney", type_="London borough"),
        GBSubdivision(code="GB-HEF", name="Herefordshire", type_="Unitary authority"),
        GBSubdivision(code="GB-HIL", name="Hillingdon", type_="London borough"),
        GBSubdivision(code="GB-HLD", name="Highland", type_="Council area"),
        GBSubdivision(code="GB-HMF", name="Hammersmith and Fulham", type_="London borough"),
        GBSubdivision(code="GB-HNS", name="Hounslow", type_="London borough"),
        GBSubdivision(code="GB-HPL", name="Hartlepool", type_="Unitary authority"),
        GBSubdivision(code="GB-HRT", name="Hertfordshire", type_="Two-tier county"),
        GBSubdivision(code="GB-HRW", name="Harrow", type_="London borough"),
        GBSubdivision(code="GB-HRY", name="Haringey", type_="London borough"),
        GBSubdivision(code="GB-IOS", name="Isles of Scilly", type_="Unitary authority"),
        GBSubdivision(code="GB-IOW", name="Isle of Wight", type_="Unitary authority"),
        GBSubdivision(code="GB-ISL", name="Islington", type_="London borough"),
        GBSubdivision(code="GB-IVC", name="Inverclyde", type_="Council area"),
        GBSubdivision(code="GB-KEC", name="Kensington and Chelsea", type_="London borough"),
        GBSubdivision(code="GB-KEN", name="Kent", type_="Two-tier county"),
        GBSubdivision(code="GB-KHL", name="Kingston upon Hull", type_="Unitary authority"),
        GBSubdivision(code="GB-KIR", name="Kirklees", type_="Metropolitan district"),
        GBSubdivision(code="GB-KTT", name="Kingston upon Thames", type_="London borough"),
        GBSubdivision(code="GB-KWL", name="Knowsley", type_="Metropolitan district"),
        GBSubdivision(code="GB-LAN", name="Lancashire", type_="Two-tier county"),
        GBSubdivision(code="GB-LBC", name="Lisburn and Castlereagh", type_="District"),
        GBSubdivision(code="GB-LBH", name="Lambeth", type_="London borough"),
        GBSubdivision(code="GB-LCE", name="Leicester", type_="Unitary authority"),
        GBSubdivision(code="GB-LDS", name="Leeds", type_="Metropolitan district"),
        GBSubdivision(code="GB-LEC", name="Leicestershire", type_="Two-tier county"),
        GBSubdivision(code="GB-LEW", name="Lewisham", type_="London borough"),
        GBSubdivision(code="GB-LIN", name="Lincolnshire", type_="Two-tier county"),
        GBSubdivision(code="GB-LIV", name="Liverpool", type_="Metropolitan district"),
        GBSubdivision(code="GB-LND", name="London, City of", type_="City corporation"),
        GBSubdivision(code="GB-LUT", name="Luton", type_="Unitary authority"),
        GBSubdivision(code="GB-MAN", name="Manchester", type_="Metropolitan district"),
        GBSubdivision(code="GB-MDB", name="Middlesbrough", type_="Unitary authority"),
        GBSubdivision(code="GB-MDW", name="Medway", type_="Unitary authority"),
        GBSubdivision(code="GB-MEA", name="Mid and East Antrim", type_="District"),
        GBSubdivision(code="GB-MIK", name="Milton Keynes", type_="Unitary authority"),
        GBSubdivision(code="GB-MLN", name="Midlothian", type_="Council area"),
        GBSubdivision(code="GB-MON", name="Monmouthshire [Sir Fynwy GB-FYN]", type_="Unitary authority"),
        GBSubdivision(code="GB-MRT", name="Merton", type_="London borough"),
        GBSubdivision(code="GB-MRY", name="Moray", type_="Council area"),
        GBSubdivision(code="GB-MTY", name="Merthyr Tydfil [Merthyr Tudful GB-MTU]", type_="Unitary authority"),
        GBSubdivision(code="GB-MUL", name="Mid-Ulster", type_="District"),
        GBSubdivision(code="GB-NAY", name="North Ayrshire", type_="Council area"),
        GBSubdivision(code="GB-NBL", name="Northumberland", type_="Unitary authority"),
        GBSubdivision(code="GB-NEL", name="North East Lincolnshire", type_="Unitary authority"),
        GBSubdivision(code="GB-NET", name="Newcastle upon Tyne", type_="Metropolitan district"),
        GBSubdivision(code="GB-NFK", name="Norfolk", type_="Two-tier county"),
        GBSubdivision(code="GB-NGM", name="Nottingham", type_="Unitary authority"),
        GBSubdivision(code="GB-NIR", name="Northern Ireland", type_="Province"),
        GBSubdivision(code="GB-NLK", name="North Lanarkshire", type_="Council area"),
        GBSubdivision(code="GB-NLN", name="North Lincolnshire", type_="Unitary authority"),
        GBSubdivision(code="GB-NMD", name="Newry, Mourne and Down", type_="District"),
        GBSubdivision(code="GB-NNH", name="North Northamptonshire", type_="Unitary authority"),
        GBSubdivision(code="GB-NSM", name="North Somerset", type_="Unitary authority"),
        GBSubdivision(
            code="GB-NTL",
            name="Neath Port Talbot [Castell-nedd Port Talbot GB-CTL]",
            type_="Unitary authority",
        ),
        GBSubdivision(code="GB-NTT", name="Nottinghamshire", type_="Two-tier county"),
        GBSubdivision(code="GB-NTY", name="North Tyneside", type_="Metropolitan district"),
        GBSubdivision(code="GB-NWM", name="Newham", type_="London borough"),
        GBSubdivision(code="GB-NWP", name="Newport [Casnewydd GB-CNW]", type_="Unitary authority"),
        GBSubdivision(code="GB-NYK", name="North Yorkshire", type_="Two-tier county"),
        GBSubdivision(code="GB-OLD", name="Oldham", type_="Metropolitan district"),
        GBSubdivision(code="GB-ORK", name="Orkney Islands", type_="Council area"),
        GBSubdivision(code="GB-OXF", name="Oxfordshire", type_="Two-tier county"),
        GBSubdivision(code="GB-PEM", name="Pembrokeshire [Sir Benfro GB-BNF]", type_="Unitary authority"),
        GBSubdivision(code="GB-PKN", name="Perth and Kinross", type_="Council area"),
        GBSubdivision(code="GB-PLY", name="Plymouth", type_="Unitary authority"),
        GBSubdivision(code="GB-POR", name="Portsmouth", type_="Unitary authority"),
        GBSubdivision(code="GB-POW", name="Powys", type_="Unitary authority"),
        GBSubdivision(code="GB-PTE", name="Peterborough", type_="Unitary authority"),
        GBSubdivision(code="GB-RCC", name="Redcar and Cleveland", type_="Unitary authority"),
        GBSubdivision(code="GB-RCH", name="Rochdale", type_="Metropolitan district"),
        GBSubdivision(code="GB-RCT", name="Rhondda Cynon Taff [Rhondda CynonTaf]", type_="Unitary authority"),
        GBSubdivision(code="GB-RDB", name="Redbridge", type_="London borough"),
        GBSubdivision(code="GB-RDG", name="Reading", type_="Unitary authority"),
        GBSubdivision(code="GB-RFW", name="Renfrewshire", type_="Council area"),
        GBSubdivision(code="GB-RIC", name="Richmond upon Thames", type_="London borough"),
        GBSubdivision(code="GB-ROT", name="Rotherham", type_="Metropolitan district"),
        GBSubdivision(code="GB-RUT", name="Rutland", type_="Unitary authority"),
        GBSubdivision(code="GB-SAW", name="Sandwell", type_="Metropolitan district"),
        GBSubdivision(code="GB-SAY", name="South Ayrshire", type_="Council area"),
        GBSubdivision(code="GB-SCB", name="Scottish Borders", type_="Council area"),
        GBSubdivision(code="GB-SCT", name="Scotland", type_="Country"),
        GBSubdivision(code="GB-SFK", name="Suffolk", type_="Two-tier county"),
        GBSubdivision(code="GB-SFT", name="Sefton", type_="Metropolitan district"),
        GBSubdivision(code="GB-SGC", name="South Gloucestershire", type_="Unitary authority"),
        GBSubdivision(code="GB-SHF", name="Sheffield", type_="Metropolitan district"),
        GBSubdivision(code="GB-SHN", name="St. Helens", type_="Metropolitan district"),
        GBSubdivision(code="GB-SHR", name="Shropshire", type_="Unitary authority"),
        GBSubdivision(code="GB-SKP", name="Stockport", type_="Metropolitan district"),
        GBSubdivision(code="GB-SLF", name="Salford", type_="Metropolitan district"),
        GBSubdivision(code="GB-SLG", name="Slough", type_="Unitary authority"),
        GBSubdivision(code="GB-SLK", name="South Lanarkshire", type_="Council area"),
        GBSubdivision(code="GB-SND", name="Sunderland", type_="Metropolitan district"),
        GBSubdivision(code="GB-SOL", name="Solihull", type_="Metropolitan district"),
        GBSubdivision(code="GB-SOM", name="Somerset", type_="Two-tier county"),
        GBSubdivision(code="GB-SOS", name="Southend-on-Sea", type_="Unitary authority"),
        GBSubdivision(code="GB-SRY", name="Surrey", type_="Two-tier county"),
        GBSubdivision(code="GB-STE", name="Stoke-on-Trent", type_="Unitary authority"),
        GBSubdivision(code="GB-STG", name="Stirling", type_="Council area"),
        GBSubdivision(code="GB-STH", name="Southampton", type_="Unitary authority"),
        GBSubdivision(code="GB-STN", name="Sutton", type_="London borough"),
        GBSubdivision(code="GB-STS", name="Staffordshire", type_="Two-tier county"),
        GBSubdivision(code="GB-STT", name="Stockton-on-Tees", type_="Unitary authority"),
        GBSubdivision(code="GB-STY", name="South Tyneside", type_="Metropolitan district"),
        GBSubdivision(code="GB-SWA", name="Swansea [Abertawe GB-ATA]", type_="Unitary authority"),
        GBSubdivision(code="GB-SWD", name="Swindon", type_="Unitary authority"),
        GBSubdivision(code="GB-SWK", name="Southwark", type_="London borough"),
        GBSubdivision(code="GB-TAM", name="Tameside", type_="Metropolitan district"),
        GBSubdivision(code="GB-TFW", name="Telford and Wrekin", type_="Unitary authority"),
        GBSubdivision(code="GB-THR", name="Thurrock", type_="Unitary authority"),
        GBSubdivision(code="GB-TOB", name="Torbay", type_="Unitary authority"),
        GBSubdivision(code="GB-TOF", name="Torfaen [Tor-faen]", type_="Unitary authority"),
        GBSubdivision(code="GB-TRF", name="Trafford", type_="Metropolitan district"),
        GBSubdivision(code="GB-TWH", name="Tower Hamlets", type_="London borough"),
        GBSubdivision(code="GB-VGL", name="Vale of Glamorgan, The [Bro Morgannwg GB-BMG]", type_="Unitary authority"),
        GBSubdivision(code="GB-WAR", name="Warwickshire", type_="Two-tier county"),
        GBSubdivision(code="GB-WBK", name="West Berkshire", type_="Unitary authority"),
        GBSubdivision(code="GB-WDU", name="West Dunbartonshire", type_="Council area"),
        GBSubdivision(code="GB-WFT", name="Waltham Forest", type_="London borough"),
        GBSubdivision(code="GB-WGN", name="Wigan", type_="Metropolitan district"),
        GBSubdivision(code="GB-WIL", name="Wiltshire", type_="Unitary authority"),
        GBSubdivision(code="GB-WKF", name="Wakefield", type_="Metropolitan district"),
        GBSubdivision(code="GB-WLL", name="Walsall", type_="Metropolitan district"),
        GBSubdivision(code="GB-WLN", name="West Lothian", type_="Council area"),
        GBSubdivision(code="GB-WLS", name="Wales [Cymru GB-CYM]", type_="Country"),
        GBSubdivision(code="GB-WLV", name="Wolverhampton", type_="Metropolitan district"),
        GBSubdivision(code="GB-WND", name="Wandsworth", type_="London borough"),
        GBSubdivision(code="GB-WNH", name="West Northamptonshire", type_="Unitary authority"),
        GBSubdivision(code="GB-WNM", name="Windsor and Maidenhead", type_="Unitary authority"),
        GBSubdivision(code="GB-WOK", name="Wokingham", type_="Unitary authority"),
        GBSubdivision(code="GB-WOR", name="Worcestershire", type_="Two-tier county"),
        GBSubdivision(code="GB-WRL", name="Wirral", type_="Metropolitan district"),
        GBSubdivision(code="GB-WRT", name="Warrington", type_="Unitary authority"),
        GBSubdivision(code="GB-WRX", name="Wrexham [Wrecsam GB-WRC]", type_="Unitary authority"),
        GBSubdivision(code="GB-WSM", name="Westminster", type_="London borough"),
        GBSubdivision(code="GB-WSX", name="West Sussex", type_="Two-tier county"),
        GBSubdivision(code="GB-YOR", name="York", type_="Unitary authority"),
        GBSubdivision(code="GB-ZET", name="Shetland Islands", type_="Council area"),
    ],
)
