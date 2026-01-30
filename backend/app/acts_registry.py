"""
acts_registry.py

Single source of truth for all NZ Acts supported by Bowen.
Used by both the backend for act detection and served to frontend via API.
"""

from typing import List, Dict, Optional

# Acts Registry - the single source of truth
ACTS_REGISTRY: Dict[str, Dict] = {
    "RTA": {
        "title": "Residential Tenancies Act 1986",
        "short_name": "RTA",
        "year": 1986,
        "keywords": ["rta", "residential tenancies", "tenancy", "tenant", "landlord", "bond", "rental", "rent"],
        "topics": ["tenancy", "bonds", "housing"],
        "url": "https://www.legislation.govt.nz/act/public/1986/0120/latest/DLM94278.html"
    },
    "ERA": {
        "title": "Employment Relations Act 2000",
        "short_name": "ERA",
        "year": 2000,
        "keywords": ["era", "employment relations", "employment", "employer", "employee", "dismissal", "redundancy", "leave", "wages", "union"],
        "topics": ["employment", "dismissal", "leave"],
        "url": "https://www.legislation.govt.nz/act/public/2000/0024/latest/DLM58317.html"
    },
    "CA": {
        "title": "Companies Act 1993",
        "short_name": "CA",
        "year": 1993,
        "keywords": ["companies act", "company", "director", "shareholder", "incorporation", "liquidation"],
        "topics": ["directors", "shareholders", "incorporation"],
        "url": "https://www.legislation.govt.nz/act/public/1993/0105/latest/DLM319570.html"
    },
    "CGA": {
        "title": "Consumer Guarantees Act 1993",
        "short_name": "CGA",
        "year": 1993,
        "keywords": ["cga", "consumer guarantees", "consumer", "refund", "repair", "guarantee"],
        "topics": ["refunds", "repairs", "guarantees"],
        "url": "https://www.legislation.govt.nz/act/public/1993/0091/latest/DLM311053.html"
    },
    "PLA": {
        "title": "Property Law Act 2007",
        "short_name": "PLA",
        "year": 2007,
        "keywords": ["pla", "property law", "mortgage", "lease", "easement", "property"],
        "topics": ["property", "mortgages", "leases"],
        "url": "https://www.legislation.govt.nz/act/public/2007/0091/latest/DLM968962.html"
    },
    "FTA": {
        "title": "Fair Trading Act 1986",
        "short_name": "FTA",
        "year": 1986,
        "keywords": ["fta", "fair trading", "misleading", "deceptive", "consumer protection"],
        "topics": ["consumer protection", "misleading conduct"],
        "url": "https://www.legislation.govt.nz/act/public/1986/0121/latest/DLM96439.html"
    },
    "PA": {
        "title": "Privacy Act 2020",
        "short_name": "PA",
        "year": 2020,
        "keywords": ["privacy act", "privacy", "personal information", "data protection", "ipp"],
        "topics": ["personal information", "data breaches"],
        "url": "https://www.legislation.govt.nz/act/public/2020/0031/latest/LMS23223.html"
    },
    "BA": {
        "title": "Building Act 2004",
        "short_name": "BA",
        "year": 2004,
        "keywords": ["building act", "building consent", "building code", "construction", "ccc", "code compliance"],
        "topics": ["consents", "code compliance"],
        "url": "https://www.legislation.govt.nz/act/public/2004/0072/latest/DLM306036.html"
    },
    "CCLA": {
        "title": "Contract and Commercial Law Act 2017",
        "short_name": "CCLA",
        "year": 2017,
        "keywords": ["ccla", "contract", "commercial law", "sale of goods", "contracts"],
        "topics": ["contracts", "sale of goods"],
        "url": "https://www.legislation.govt.nz/act/public/2017/0005/latest/DLM6844033.html"
    },
    "RMA": {
        "title": "Resource Management Act 1991",
        "short_name": "RMA",
        "year": 1991,
        "keywords": ["rma", "resource management", "resource consent", "environmental", "environment", "planning"],
        "topics": ["environment", "resource consents"],
        "url": "https://www.legislation.govt.nz/act/public/1991/0069/latest/DLM230265.html"
    },
    "CA1961": {
        "title": "Crimes Act 1961",
        "short_name": "CA1961",
        "year": 1961,
        "keywords": ["crimes act", "criminal", "crime", "offence", "sentencing"],
        "topics": ["criminal offences", "sentencing"],
        "url": "https://www.legislation.govt.nz/act/public/1961/0043/latest/DLM327382.html"
    },
    "HSWA": {
        "title": "Health and Safety at Work Act 2015",
        "short_name": "HSWA",
        "year": 2015,
        "keywords": ["hswa", "health and safety", "workplace safety", "pcbu", "worksafe"],
        "topics": ["workplace safety", "PCBU duties"],
        "url": "https://www.legislation.govt.nz/act/public/2015/0070/latest/DLM5976660.html"
    },
    "HRA": {
        "title": "Human Rights Act 1993",
        "short_name": "HRA",
        "year": 1993,
        "keywords": ["human rights", "discrimination", "equality", "hrc"],
        "topics": ["discrimination", "equality"],
        "url": "https://www.legislation.govt.nz/act/public/1993/0082/latest/DLM304212.html"
    },
    "ITA": {
        "title": "Income Tax Act 2007",
        "short_name": "ITA",
        "year": 2007,
        "keywords": ["income tax", "tax", "ird", "deduction", "taxable income"],
        "topics": ["tax", "deductions", "income"],
        "url": "https://www.legislation.govt.nz/act/public/2007/0097/latest/DLM1512301.html"
    },
    "LTA": {
        "title": "Land Transport Act 1998",
        "short_name": "LTA",
        "year": 1998,
        "keywords": ["land transport", "driving", "licence", "traffic", "road"],
        "topics": ["driving", "licences", "traffic"],
        "url": "https://www.legislation.govt.nz/act/public/1998/0110/latest/DLM433613.html"
    },
    "IA": {
        "title": "Immigration Act 2009",
        "short_name": "IA",
        "year": 2009,
        "keywords": ["immigration", "visa", "residence", "deportation", "migrant"],
        "topics": ["visas", "residence", "deportation"],
        "url": "https://www.legislation.govt.nz/act/public/2009/0051/latest/DLM1440303.html"
    },
    "TA": {
        "title": "Trusts Act 2019",
        "short_name": "TA",
        "year": 2019,
        "keywords": ["trusts act", "trust", "trustee", "beneficiary", "settlor"],
        "topics": ["trusts", "trustees", "beneficiaries"],
        "url": "https://www.legislation.govt.nz/act/public/2019/0038/latest/LMS82334.html"
    },
    "INSA": {
        "title": "Insolvency Act 2006",
        "short_name": "INSA",
        "year": 2006,
        "keywords": ["insolvency", "bankruptcy", "liquidation", "bankrupt"],
        "topics": ["bankruptcy", "liquidation"],
        "url": "https://www.legislation.govt.nz/act/public/2006/0055/latest/DLM385299.html"
    },
    "CRA": {
        "title": "Copyright Act 1994",
        "short_name": "CRA",
        "year": 1994,
        "keywords": ["copyright", "intellectual property", "ip", "infringement"],
        "topics": ["copyright", "intellectual property"],
        "url": "https://www.legislation.govt.nz/act/public/1994/0143/latest/DLM345634.html"
    },
    "CCCFA": {
        "title": "Credit Contracts and Consumer Finance Act 2003",
        "short_name": "CCCFA",
        "year": 2003,
        "keywords": ["cccfa", "credit", "loan", "consumer finance", "interest"],
        "topics": ["loans", "credit", "interest"],
        "url": "https://www.legislation.govt.nz/act/public/2003/0052/latest/DLM211512.html"
    },
    "OIA": {
        "title": "Official Information Act 1982",
        "short_name": "OIA",
        "year": 1982,
        "keywords": ["oia", "official information", "government information", "disclosure"],
        "topics": ["government", "requests", "disclosure"],
        "url": "https://www.legislation.govt.nz/act/public/1982/0156/latest/DLM64785.html"
    },
    "FVA": {
        "title": "Family Violence Act 2018",
        "short_name": "FVA",
        "year": 2018,
        "keywords": ["family violence", "domestic violence", "protection order", "abuse"],
        "topics": ["protection orders", "domestic violence"],
        "url": "https://www.legislation.govt.nz/act/public/2018/0046/latest/LMS112966.html"
    },
    "ACA": {
        "title": "Accident Compensation Act 2001",
        "short_name": "ACA",
        "year": 2001,
        "keywords": ["acc", "accident compensation", "injury", "compensation"],
        "topics": ["ACC", "injury", "compensation"],
        "url": "https://www.legislation.govt.nz/act/public/2001/0049/latest/DLM99494.html"
    },
    "FMCA": {
        "title": "Financial Markets Conduct Act 2013",
        "short_name": "FMCA",
        "year": 2013,
        "keywords": ["fmca", "financial markets", "securities", "investment", "fma"],
        "topics": ["securities", "investment", "disclosure"],
        "url": "https://www.legislation.govt.nz/act/public/2013/0069/latest/DLM4090578.html"
    },
    "HDCA": {
        "title": "Harmful Digital Communications Act 2015",
        "short_name": "HDCA",
        "year": 2015,
        "keywords": ["hdca", "harmful digital", "cyberbullying", "online harassment", "netsafe"],
        "topics": ["cyberbullying", "online harassment"],
        "url": "https://www.legislation.govt.nz/act/public/2015/0063/latest/whole.html"
    },
    "UTA": {
        "title": "Unit Titles Act 2010",
        "short_name": "UTA",
        "year": 2010,
        "keywords": ["unit titles", "body corporate", "apartment", "strata"],
        "topics": ["body corporate", "apartments"],
        "url": "https://www.legislation.govt.nz/act/public/2010/0022/latest/DLM1160440.html"
    },
    "LGA": {
        "title": "Local Government Act 2002",
        "short_name": "LGA",
        "year": 2002,
        "keywords": ["local government", "council", "rates", "bylaws"],
        "topics": ["councils", "rates", "bylaws"],
        "url": "https://www.legislation.govt.nz/act/public/2002/0084/latest/DLM170873.html"
    },
    "FCA": {
        "title": "Family Court Act 1980",
        "short_name": "FCA",
        "year": 1980,
        "keywords": ["family court", "family proceedings"],
        "topics": ["family court", "jurisdiction"],
        "url": "https://www.legislation.govt.nz/act/public/1980/0161/latest/DLM42254.html"
    },
    "CORA": {
        "title": "Coroners Act 2006",
        "short_name": "CORA",
        "year": 2006,
        "keywords": ["coroner", "inquest", "death inquiry"],
        "topics": ["inquests", "death inquiries"],
        "url": "https://www.legislation.govt.nz/act/public/2006/0038/latest/DLM377057.html"
    },
    "SOGA": {
        "title": "Sale of Goods Act 1908",
        "short_name": "SOGA",
        "year": 1908,
        "keywords": ["sale of goods", "goods", "buyer", "seller"],
        "topics": ["sale", "goods", "contracts"],
        "url": "https://www.legislation.govt.nz/act/public/1908/0168/latest/DLM173958.html"
    },
    "EA": {
        "title": "Education Act 1989",
        "short_name": "EA",
        "year": 1989,
        "keywords": ["education act", "school", "student", "curriculum", "teacher"],
        "topics": ["schools", "students", "curriculum"],
        "url": "https://www.legislation.govt.nz/act/public/1989/0080/latest/DLM175959.html"
    },
    "CONST": {
        "title": "Constitution Act 1986",
        "short_name": "CONST",
        "year": 1986,
        "keywords": ["constitution", "parliament", "sovereignty", "executive", "crown"],
        "topics": ["parliament", "sovereignty", "executive"],
        "url": "https://www.legislation.govt.nz/act/public/1986/0114/latest/DLM94204.html"
    },
    "ELEC": {
        "title": "Electoral Act 1993",
        "short_name": "ELEC",
        "year": 1993,
        "keywords": ["electoral", "election", "voting", "mmp", "parliament"],
        "topics": ["voting", "elections", "parliament"],
        "url": "https://www.legislation.govt.nz/act/public/1993/0087/latest/DLM307519.html"
    },
    "CITZ": {
        "title": "Citizenship Act 1977",
        "short_name": "CITZ",
        "year": 1977,
        "keywords": ["citizenship", "naturalisation", "citizen"],
        "topics": ["citizenship", "naturalisation"],
        "url": "https://www.legislation.govt.nz/act/public/1977/0061/latest/DLM443684.html"
    },
    "AML": {
        "title": "Anti-Money Laundering and Countering Financing of Terrorism Act 2009",
        "short_name": "AML",
        "year": 2009,
        "keywords": ["aml", "anti-money laundering", "money laundering", "terrorism financing", "kyc"],
        "topics": ["money laundering", "terrorism financing", "reporting"],
        "url": "https://www.legislation.govt.nz/act/public/2009/0035/latest/DLM2140700.html"
    },
    "TMA": {
        "title": "Trade Marks Act 2002",
        "short_name": "TMA",
        "year": 2002,
        "keywords": ["trade mark", "trademark", "brand", "registration"],
        "topics": ["trade marks", "registration", "infringement"],
        "url": "https://www.legislation.govt.nz/act/public/2002/0049/latest/DLM164240.html"
    },
    "PATA": {
        "title": "Patents Act 2013",
        "short_name": "PATA",
        "year": 2013,
        "keywords": ["patent", "invention", "iponz"],
        "topics": ["patents", "inventions", "intellectual property"],
        "url": "https://www.legislation.govt.nz/act/public/2013/0068/latest/DLM1419043.html"
    },
    "CCRA": {
        "title": "Climate Change Response Act 2002",
        "short_name": "CCRA",
        "year": 2002,
        "keywords": ["climate change", "emissions", "carbon", "ets"],
        "topics": ["emissions", "carbon", "climate"],
        "url": "https://www.legislation.govt.nz/act/public/2002/0040/latest/DLM158584.html"
    },
    "CONS": {
        "title": "Conservation Act 1987",
        "short_name": "CONS",
        "year": 1987,
        "keywords": ["conservation", "doc", "protected area", "national park"],
        "topics": ["conservation", "DOC", "protected areas"],
        "url": "https://www.legislation.govt.nz/act/public/1987/0065/latest/DLM103610.html"
    },
    "PSA": {
        "title": "Public Service Act 2020",
        "short_name": "PSA",
        "year": 2020,
        "keywords": ["public service", "government agency", "state sector"],
        "topics": ["public service", "government agencies"],
        "url": "https://www.legislation.govt.nz/act/public/2020/0040/latest/LMS106159.html"
    },
    "FENZ": {
        "title": "Fire and Emergency New Zealand Act 2017",
        "short_name": "FENZ",
        "year": 2017,
        "keywords": ["fire", "emergency", "fenz", "fire service", "rescue"],
        "topics": ["fire", "emergency", "rescue"],
        "url": "https://www.legislation.govt.nz/act/public/2017/0017/latest/DLM6712701.html"
    },
    "PFA": {
        "title": "Public Finance Act 1989",
        "short_name": "PFA",
        "year": 1989,
        "keywords": ["public finance", "budget", "appropriation", "crown accounts"],
        "topics": ["budget", "appropriation", "crown"],
        "url": "https://www.legislation.govt.nz/act/public/1989/0044/latest/DLM160809.html"
    },
    "DCA": {
        "title": "District Courts Act 1947",
        "short_name": "DCA",
        "year": 1947,
        "keywords": ["district court", "district courts"],
        "topics": ["district court", "jurisdiction"],
        "url": "https://www.legislation.govt.nz/act/public/1947/0016/latest/DLM242776.html"
    },
    "BSA": {
        "title": "Biosecurity Act 1993",
        "short_name": "BSA",
        "year": 1993,
        "keywords": ["biosecurity", "pest", "quarantine", "mpi"],
        "topics": ["biosecurity", "pest", "quarantine"],
        "url": "https://www.legislation.govt.nz/act/public/1993/0095/latest/DLM314623.html"
    },
    "FA": {
        "title": "Fisheries Act 1996",
        "short_name": "FA",
        "year": 1996,
        "keywords": ["fisheries", "fishing", "quota", "marine"],
        "topics": ["fishing", "quota", "marine"],
        "url": "https://www.legislation.govt.nz/act/public/1996/0088/latest/DLM394192.html"
    },
    "HSNO": {
        "title": "Hazardous Substances and New Organisms Act 1996",
        "short_name": "HSNO",
        "year": 1996,
        "keywords": ["hsno", "hazardous substances", "chemicals", "gmo", "new organisms"],
        "topics": ["hazardous", "chemicals", "GMO"],
        "url": "https://www.legislation.govt.nz/act/public/1996/0030/latest/DLM381222.html"
    },
    "FCAM": {
        "title": "Freedom Camping Act 2011",
        "short_name": "FCAM",
        "year": 2011,
        "keywords": ["freedom camping", "camping", "campervan"],
        "topics": ["camping", "vehicles", "local authority"],
        "url": "https://www.legislation.govt.nz/act/public/2011/0061/latest/DLM3742828.html"
    },
    "HA": {
        "title": "Health Act 1956",
        "short_name": "HA",
        "year": 1956,
        "keywords": ["health act", "public health", "sanitation", "disease"],
        "topics": ["public health", "sanitation", "disease"],
        "url": "https://www.legislation.govt.nz/act/public/1956/0065/latest/DLM305840.html"
    },
    "MA": {
        "title": "Medicines Act 1981",
        "short_name": "MA",
        "year": 1981,
        "keywords": ["medicines", "pharmacy", "prescription", "drug"],
        "topics": ["medicine", "pharmacy", "prescription"],
        "url": "https://www.legislation.govt.nz/act/public/1981/0118/latest/DLM53790.html"
    },
    "SEA": {
        "title": "Smokefree Environments Act 1990",
        "short_name": "SEA",
        "year": 1990,
        "keywords": ["smokefree", "smoking", "tobacco", "vaping"],
        "topics": ["smoking", "tobacco", "vaping"],
        "url": "https://www.legislation.govt.nz/act/public/1990/0108/latest/DLM223191.html"
    },
    "CDEM": {
        "title": "Civil Defence Emergency Management Act 2002",
        "short_name": "CDEM",
        "year": 2002,
        "keywords": ["civil defence", "emergency management", "cdem", "disaster", "emergency"],
        "topics": ["civil defence", "emergency", "disaster response"],
        "url": "https://www.legislation.govt.nz/act/public/2002/0033/latest/DLM149789.html"
    },
    "HPCA": {
        "title": "Health Practitioners Competence Assurance Act 2003",
        "short_name": "HPCA",
        "year": 2003,
        "keywords": ["health practitioners", "medical registration", "competence", "hpca"],
        "topics": ["health practitioners", "registration", "competence"],
        "url": "https://www.legislation.govt.nz/act/public/2003/0048/latest/DLM203312.html"
    },
    "HNZPT": {
        "title": "Heritage New Zealand Pouhere Taonga Act 2014",
        "short_name": "HNZPT",
        "year": 2014,
        "keywords": ["heritage", "pouhere taonga", "historic places", "archaeological"],
        "topics": ["heritage", "historic places", "archaeology"],
        "url": "https://www.legislation.govt.nz/act/public/2014/0026/latest/DLM4005414.html"
    },
    "LEA": {
        "title": "Local Electoral Act 2001",
        "short_name": "LEA",
        "year": 2001,
        "keywords": ["local electoral", "local elections", "council elections", "sts voting"],
        "topics": ["local elections", "voting", "councils"],
        "url": "https://www.legislation.govt.nz/act/public/2001/0035/latest/DLM93301.html"
    },
    "LGA1974": {
        "title": "Local Government Act 1974",
        "short_name": "LGA1974",
        "year": 1974,
        "keywords": ["local government 1974", "roads", "drainage", "public works"],
        "topics": ["local government", "roads", "public works"],
        "url": "https://www.legislation.govt.nz/act/public/1974/0066/latest/DLM415532.html"
    },
    "LGACA": {
        "title": "Local Government (Auckland Council) Act 2009",
        "short_name": "LGACA",
        "year": 2009,
        "keywords": ["auckland council", "auckland supercity", "auckland local government"],
        "topics": ["Auckland", "council", "local government"],
        "url": "https://www.legislation.govt.nz/act/public/2009/0032/latest/DLM2044909.html"
    },
    "LGOIMA": {
        "title": "Local Government Official Information and Meetings Act 1987",
        "short_name": "LGOIMA",
        "year": 1987,
        "keywords": ["lgoima", "local government official information", "council meetings", "council information"],
        "topics": ["official information", "meetings", "councils"],
        "url": "https://www.legislation.govt.nz/act/public/1987/0174/latest/DLM122242.html"
    },
    "LGRA": {
        "title": "Local Government (Rating) Act 2002",
        "short_name": "LGRA",
        "year": 2002,
        "keywords": ["rating", "rates", "council rates", "property rates"],
        "topics": ["rates", "rating", "property tax"],
        "url": "https://www.legislation.govt.nz/act/public/2002/0006/latest/DLM131394.html"
    },
    "MFA": {
        "title": "Maori Fisheries Act 2004",
        "short_name": "MFA",
        "year": 2004,
        "keywords": ["maori fisheries", "te ohu kaimoana", "iwi fisheries", "settlement assets"],
        "topics": ["Maori fisheries", "Te Ohu Kaimoana", "iwi"],
        "url": "https://www.legislation.govt.nz/act/public/2004/0078/latest/DLM311464.html"
    },
    "MCAA": {
        "title": "Marine and Coastal Area (Takutai Moana) Act 2011",
        "short_name": "MCAA",
        "year": 2011,
        "keywords": ["marine coastal area", "takutai moana", "foreshore seabed", "customary rights"],
        "topics": ["marine area", "coastal", "customary rights"],
        "url": "https://www.legislation.govt.nz/act/public/2011/0003/latest/DLM3213131.html"
    },
    "NWMWR": {
        "title": "Nga Wai o Maniapoto (Waipa River) Act 2012",
        "short_name": "NWMWR",
        "year": 2012,
        "keywords": ["maniapoto", "waipa river", "nga wai o maniapoto"],
        "topics": ["Waipa River", "Maniapoto", "treaty settlement"],
        "url": "https://www.legislation.govt.nz/act/public/2012/0029/latest/DLM3335204.html"
    },
    "NTCS": {
        "title": "Ngai Tahu Claims Settlement Act 1998",
        "short_name": "NTCS",
        "year": 1998,
        "keywords": ["ngai tahu", "ngai tahu settlement", "south island iwi"],
        "topics": ["Ngai Tahu", "treaty settlement", "South Island"],
        "url": "https://www.legislation.govt.nz/act/public/1998/0097/latest/DLM429090.html"
    },
    "NTRTA": {
        "title": "Ngati Tuwharetoa, Raukawa, and Te Arawa River Iwi Waikato River Act 2010",
        "short_name": "NTRTA",
        "year": 2010,
        "keywords": ["ngati tuwharetoa", "raukawa", "te arawa", "waikato river"],
        "topics": ["Waikato River", "river iwi", "treaty settlement"],
        "url": "https://www.legislation.govt.nz/act/public/2010/0119/latest/DLM2921815.html"
    },
    "OTA": {
        "title": "Oranga Tamariki Act 1989",
        "short_name": "OTA",
        "year": 1989,
        "keywords": ["oranga tamariki", "children young persons", "child protection", "youth justice", "cyf"],
        "topics": ["child protection", "youth justice", "welfare"],
        "url": "https://www.legislation.govt.nz/act/public/1989/0024/latest/DLM147088.html"
    },
    "PA1993": {
        "title": "Privacy Act 1993",
        "short_name": "PA1993",
        "year": 1993,
        "keywords": ["privacy 1993", "old privacy act", "information privacy"],
        "topics": ["privacy", "personal information", "data protection"],
        "url": "https://www.legislation.govt.nz/act/public/1993/0028/latest/DLM296639.html"
    },
    "RRA": {
        "title": "Rates Rebate Act 1973",
        "short_name": "RRA",
        "year": 1973,
        "keywords": ["rates rebate", "rates relief", "low income rates"],
        "topics": ["rates rebate", "low income", "relief"],
        "url": "https://www.legislation.govt.nz/act/public/1973/0005/latest/DLM409766.html"
    },
    "RVA": {
        "title": "Rating Valuations Act 1998",
        "short_name": "RVA",
        "year": 1998,
        "keywords": ["rating valuations", "property valuation", "qv", "valuation roll"],
        "topics": ["valuations", "property", "rating"],
        "url": "https://www.legislation.govt.nz/act/public/1998/0069/latest/DLM427297.html"
    },
    "RA": {
        "title": "Reserves Act 1977",
        "short_name": "RA",
        "year": 1977,
        "keywords": ["reserves", "reserve land", "recreation reserves", "scenic reserves"],
        "topics": ["reserves", "recreation", "conservation"],
        "url": "https://www.legislation.govt.nz/act/public/1977/0066/latest/DLM444305.html"
    },
    "TAT": {
        "title": "Te Awa Tupua (Whanganui River Claims Settlement) Act 2017",
        "short_name": "TAT",
        "year": 2017,
        "keywords": ["te awa tupua", "whanganui river", "river personhood", "whanganui settlement"],
        "topics": ["Whanganui River", "legal personhood", "treaty settlement"],
        "url": "https://www.legislation.govt.nz/act/public/2017/0007/latest/DLM6830851.html"
    },
    "TRMA": {
        "title": "Te Ture mo Te Reo Maori 2016 (Maori Language Act)",
        "short_name": "TRMA",
        "year": 2016,
        "keywords": ["te reo maori", "maori language", "te taura whiri", "te matawai"],
        "topics": ["Te Reo Maori", "language", "revitalisation"],
        "url": "https://www.legislation.govt.nz/act/public/2016/0017/latest/DLM6174509.html"
    },
    "TRNT": {
        "title": "Te Runanga o Ngai Tahu Act 1996",
        "short_name": "TRNT",
        "year": 1996,
        "keywords": ["te runanga o ngai tahu", "ngai tahu governance", "ngai tahu runanga"],
        "topics": ["Ngai Tahu", "governance", "iwi"],
        "url": "https://www.legislation.govt.nz/act/public/1996/0001/latest/DLM371876.html"
    },
    "TTWM": {
        "title": "Te Ture Whenua Maori Act 1993 (Maori Land Act)",
        "short_name": "TTWM",
        "year": 1993,
        "keywords": ["te ture whenua", "maori land", "maori land court", "whenua maori"],
        "topics": ["Maori land", "land court", "succession"],
        "url": "https://www.legislation.govt.nz/act/public/1993/0004/latest/DLM289882.html"
    },
    "TUA": {
        "title": "Te Urewera Act 2014",
        "short_name": "TUA",
        "year": 2014,
        "keywords": ["te urewera", "tuhoe", "urewera national park"],
        "topics": ["Te Urewera", "Tuhoe", "treaty settlement"],
        "url": "https://www.legislation.govt.nz/act/public/2014/0051/latest/DLM6183601.html"
    },
    "TOWA": {
        "title": "Treaty of Waitangi Act 1975",
        "short_name": "TOWA",
        "year": 1975,
        "keywords": ["treaty of waitangi", "waitangi tribunal", "treaty claims"],
        "topics": ["Treaty of Waitangi", "Waitangi Tribunal", "claims"],
        "url": "https://www.legislation.govt.nz/act/public/1975/0114/latest/DLM435368.html"
    },
    "TOWFS": {
        "title": "Treaty of Waitangi (Fisheries Claims) Settlement Act 1992",
        "short_name": "TOWFS",
        "year": 1992,
        "keywords": ["sealord deal", "fisheries settlement", "treaty fisheries"],
        "topics": ["fisheries settlement", "Sealord", "Treaty"],
        "url": "https://www.legislation.govt.nz/act/public/1992/0121/latest/DLM281433.html"
    },
    "WRCS": {
        "title": "Waikato Raupatu Claims Settlement Act 1995",
        "short_name": "WRCS",
        "year": 1995,
        "keywords": ["waikato raupatu", "tainui settlement", "waikato-tainui"],
        "topics": ["Waikato-Tainui", "raupatu", "treaty settlement"],
        "url": "https://www.legislation.govt.nz/act/public/1995/0058/latest/DLM370102.html"
    },
    "WTWR": {
        "title": "Waikato-Tainui Raupatu Claims (Waikato River) Settlement Act 2010",
        "short_name": "WTWR",
        "year": 2010,
        "keywords": ["waikato river settlement", "waikato-tainui river", "river settlement"],
        "topics": ["Waikato River", "Waikato-Tainui", "river settlement"],
        "url": "https://www.legislation.govt.nz/act/public/2010/0024/latest/DLM1630002.html"
    },
}


def detect_act_from_query(query: str) -> Optional[str]:
    """Detect if user is asking about a specific Act using the registry."""
    query_lower = query.lower()

    for short_name, act_info in ACTS_REGISTRY.items():
        if any(kw in query_lower for kw in act_info["keywords"]):
            # Return the base name for filtering (e.g., "Residential Tenancies")
            title = act_info["title"]
            # Extract the base name (without year)
            base_name = title.rsplit(" Act", 1)[0] if " Act" in title else title
            return base_name

    return None


def get_all_acts() -> List[Dict]:
    """Get all acts as a list for the API."""
    return [
        {
            "short_name": short_name,
            "title": info["title"],
            "year": info["year"],
            "topics": info["topics"],
            "url": info["url"]
        }
        for short_name, info in ACTS_REGISTRY.items()
    ]


def get_act_by_short_name(short_name: str) -> Optional[Dict]:
    """Get a specific act by its short name."""
    return ACTS_REGISTRY.get(short_name.upper())
