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
        "topics": ["tenancy", "rental", "bond", "landlord", "tenant", "housing"],
        "url": "https://www.legislation.govt.nz/act/public/1986/0120/latest/DLM94278.html"
    },
    "ERA": {
        "title": "Employment Relations Act 2000",
        "short_name": "ERA",
        "year": 2000,
        "keywords": ["era", "employment relations", "employment", "employer", "employee", "dismissal", "redundancy", "leave", "wages", "union"],
        "topics": ["employment", "workplace", "union", "dismissal", "leave", "wages"],
        "url": "https://www.legislation.govt.nz/act/public/2000/0024/latest/DLM58317.html"
    },
    "CA": {
        "title": "Companies Act 1993",
        "short_name": "CA",
        "year": 1993,
        "keywords": ["companies act", "company", "director", "shareholder", "incorporation", "liquidation"],
        "topics": ["company", "director", "shareholder", "incorporation", "liquidation"],
        "url": "https://www.legislation.govt.nz/act/public/1993/0105/latest/DLM319570.html"
    },
    "FTA": {
        "title": "Fair Trading Act 1986",
        "short_name": "FTA",
        "year": 1986,
        "keywords": ["fta", "fair trading", "misleading", "deceptive", "consumer protection", "consumer"],
        "topics": ["consumer protection", "misleading conduct", "fair trading"],
        "url": "https://www.legislation.govt.nz/act/public/1986/0121/latest/DLM96439.html"
    },
    "PLA": {
        "title": "Property Law Act 2007",
        "short_name": "PLA",
        "year": 2007,
        "keywords": ["pla", "property law", "mortgage", "lease", "easement", "property"],
        "topics": ["property transactions", "mortgages", "leases", "easements"],
        "url": "https://www.legislation.govt.nz/act/public/2007/0091/latest/DLM968962.html"
    },
    "PA": {
        "title": "Privacy Act 2020",
        "short_name": "PA",
        "year": 2020,
        "keywords": ["privacy act", "privacy", "personal information", "data protection", "ipp"],
        "topics": ["privacy", "personal information", "data protection"],
        "url": "https://www.legislation.govt.nz/act/public/2020/0031/latest/LMS23223.html"
    },
    "BA": {
        "title": "Building Act 2004",
        "short_name": "BA",
        "year": 2004,
        "keywords": ["building act", "building consent", "building code", "construction", "ccc", "code compliance"],
        "topics": ["building", "construction", "consent", "code compliance"],
        "url": "https://www.legislation.govt.nz/act/public/2004/0072/latest/DLM306036.html"
    },
    "CCLA": {
        "title": "Contract and Commercial Law Act 2017",
        "short_name": "CCLA",
        "year": 2017,
        "keywords": ["ccla", "contract", "commercial law", "sale of goods", "contracts"],
        "topics": ["contracts", "commercial law", "sale of goods"],
        "url": "https://www.legislation.govt.nz/act/public/2017/0005/latest/DLM6844033.html"
    },
    "RMA": {
        "title": "Resource Management Act 1991",
        "short_name": "RMA",
        "year": 1991,
        "keywords": ["rma", "resource management", "resource consent", "environmental", "environment", "planning"],
        "topics": ["environmental management", "resource consents", "planning"],
        "url": "https://www.legislation.govt.nz/act/public/1991/0069/latest/DLM230265.html"
    }
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
            # Handle special cases
            if "Resource Management" in title:
                return "Resource Management"
            elif "Residential Tenancies" in title:
                return "Residential Tenancies"
            elif "Employment Relations" in title:
                return "Employment Relations"
            elif "Companies" in title:
                return "Companies"
            elif "Fair Trading" in title:
                return "Fair Trading"
            elif "Privacy" in title:
                return "Privacy"
            elif "Building" in title:
                return "Building"
            elif "Property Law" in title:
                return "Property Law"
            elif "Contract and Commercial" in title:
                return "Contract and Commercial"
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
