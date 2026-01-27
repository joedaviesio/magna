#!/usr/bin/env python3
"""
parse_legislation.py

Parses HTML files from legislation.govt.nz and extracts structured content.
Outputs JSON files with sections, definitions, and metadata.

Run from the magna root directory:
    cd ~/Desktop/magna
    python backend/scripts/parse_legislation.py
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional


# Configuration - paths relative to magna root
RAW_HTML_DIR = Path("data/raw/html")
OUTPUT_DIR = Path("data/processed/json")

# Act metadata - maps filename to metadata
ACT_METADATA = {
    "residential-tenancies-1986.html": {
        "title": "Residential Tenancies Act 1986",
        "year": 1986,
        "number": 120,
        "url": "https://www.legislation.govt.nz/act/public/1986/0120/latest/whole.html",
        "short_name": "RTA",
        "topics": ["tenancy", "rental", "landlord", "tenant", "bond", "housing"]
    },
    "employment-relations-2000.html": {
        "title": "Employment Relations Act 2000",
        "year": 2000,
        "number": 24,
        "url": "https://www.legislation.govt.nz/act/public/2000/0024/latest/whole.html",
        "short_name": "ERA",
        "topics": ["employment", "workplace", "union", "dismissal", "leave", "wages"]
    },
    "companies-1993.html": {
        "title": "Companies Act 1993",
        "year": 1993,
        "number": 105,
        "url": "https://www.legislation.govt.nz/act/public/1993/0105/latest/whole.html",
        "short_name": "CA",
        "topics": ["company", "director", "shareholder", "incorporation", "liquidation"]
    },
    "consumer-guarantees-1993.html": {
        "title": "Consumer Guarantees Act 1993",
        "year": 1993,
        "number": 28,
        "url": "https://www.legislation.govt.nz/act/public/1993/0028/latest/whole.html",
        "short_name": "CGA",
        "topics": ["consumer", "guarantee", "refund", "repair", "goods", "services"]
    },
    "property-law-2007.html": {
        "title": "Property Law Act 2007",
        "year": 2007,
        "number": 91,
        "url": "https://www.legislation.govt.nz/act/public/2007/0091/latest/whole.html",
        "short_name": "PLA",
        "topics": ["property", "land", "mortgage", "lease", "covenant", "easement"]
    },
    "fair-trading-1986.html": {
        "title": "Fair Trading Act 1986",
        "year": 1986,
        "number": 121,
        "url": "https://www.legislation.govt.nz/act/public/1986/0121/latest/whole.html",
        "short_name": "FTA",
        "topics": ["consumer", "misleading", "deceptive", "unfair", "trade", "advertising"]
    },
    "privacy-2020.html": {
        "title": "Privacy Act 2020",
        "year": 2020,
        "number": 31,
        "url": "https://www.legislation.govt.nz/act/public/2020/0031/latest/whole.html",
        "short_name": "PA",
        "topics": ["privacy", "personal information", "data", "breach", "access"]
    },
    "privacy-1993.html": {
        "title": "Privacy Act 1993",
        "year": 1993,
        "number": 28,
        "url": "https://www.legislation.govt.nz/act/public/1993/0028/latest/whole.html",
        "short_name": "PA1993",
        "topics": ["privacy", "personal information", "data", "principles"]
    },
    "building-2004.html": {
        "title": "Building Act 2004",
        "year": 2004,
        "number": 72,
        "url": "https://www.legislation.govt.nz/act/public/2004/0072/latest/whole.html",
        "short_name": "BA",
        "topics": ["building", "consent", "code", "construction", "inspection"]
    },
    "contract-commercial-law-2017.html": {
        "title": "Contract and Commercial Law Act 2017",
        "year": 2017,
        "number": 5,
        "url": "https://www.legislation.govt.nz/act/public/2017/0005/latest/whole.html",
        "short_name": "CCLA",
        "topics": ["contract", "sale", "goods", "carriage", "mercantile", "privity"]
    },
    "resource-management-1991.html": {
        "title": "Resource Management Act 1991",
        "year": 1991,
        "number": 69,
        "url": "https://www.legislation.govt.nz/act/public/1991/0069/latest/whole.html",
        "short_name": "RMA",
        "topics": ["environment", "resource consent", "planning", "land use", "subdivision"]
    },
    "crimes-1961.html": {
        "title": "Crimes Act 1961",
        "year": 1961,
        "number": 43,
        "url": "https://www.legislation.govt.nz/act/public/1961/0043/latest/whole.html",
        "short_name": "CA1961",
        "topics": ["criminal", "offence", "murder", "assault", "theft", "fraud", "sentence"]
    },
    "health-safety-work-2015.html": {
        "title": "Health and Safety at Work Act 2015",
        "year": 2015,
        "number": 70,
        "url": "https://www.legislation.govt.nz/act/public/2015/0070/latest/whole.html",
        "short_name": "HSWA",
        "topics": ["workplace", "safety", "health", "PCBU", "worker", "hazard", "risk"]
    },
    "human-rights-1993.html": {
        "title": "Human Rights Act 1993",
        "year": 1993,
        "number": 82,
        "url": "https://www.legislation.govt.nz/act/public/1993/0082/latest/whole.html",
        "short_name": "HRA",
        "topics": ["discrimination", "human rights", "equality", "complaint", "tribunal"]
    },
    "income-tax-2007.html": {
        "title": "Income Tax Act 2007",
        "year": 2007,
        "number": 97,
        "url": "https://www.legislation.govt.nz/act/public/2007/0097/latest/whole.html",
        "short_name": "ITA",
        "topics": ["tax", "income", "deduction", "GST", "business", "investment"]
    },
    "land-transport-1998.html": {
        "title": "Land Transport Act 1998",
        "year": 1998,
        "number": 110,
        "url": "https://www.legislation.govt.nz/act/public/1998/0110/latest/whole.html",
        "short_name": "LTA",
        "topics": ["driving", "licence", "vehicle", "road", "traffic", "transport"]
    },
    "immigration-2009.html": {
        "title": "Immigration Act 2009",
        "year": 2009,
        "number": 51,
        "url": "https://www.legislation.govt.nz/act/public/2009/0051/latest/whole.html",
        "short_name": "IA",
        "topics": ["visa", "immigration", "deportation", "residence", "refugee", "border"]
    },
    "trusts-2019.html": {
        "title": "Trusts Act 2019",
        "year": 2019,
        "number": 38,
        "url": "https://www.legislation.govt.nz/act/public/2019/0038/latest/whole.html",
        "short_name": "TA",
        "topics": ["trust", "trustee", "beneficiary", "settlement", "fiduciary"]
    },
    "insolvency-2006.html": {
        "title": "Insolvency Act 2006",
        "year": 2006,
        "number": 55,
        "url": "https://www.legislation.govt.nz/act/public/2006/0055/latest/whole.html",
        "short_name": "INSA",
        "topics": ["bankruptcy", "insolvency", "debt", "creditor", "liquidation"]
    },
    "copyright-1994.html": {
        "title": "Copyright Act 1994",
        "year": 1994,
        "number": 143,
        "url": "https://www.legislation.govt.nz/act/public/1994/0143/latest/whole.html",
        "short_name": "CRA",
        "topics": ["copyright", "intellectual property", "infringement", "licence", "moral rights"]
    },
    "credit-contracts-2003.html": {
        "title": "Credit Contracts and Consumer Finance Act 2003",
        "year": 2003,
        "number": 52,
        "url": "https://www.legislation.govt.nz/act/public/2003/0052/latest/whole.html",
        "short_name": "CCCFA",
        "topics": ["credit", "loan", "interest", "consumer finance", "lender", "borrower"]
    },
}


def clean_text(text: str) -> str:
    """Clean extracted text by normalizing whitespace."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def extract_section_number(heading_text: str) -> Optional[str]:
    """Extract section number from heading text."""
    patterns = [
        r'^(\d+[A-Z]*)\s',
        r'^Section\s+(\d+[A-Z]*)',
        r'^(Schedule\s+\d+[A-Z]*)',
    ]
    for pattern in patterns:
        match = re.match(pattern, heading_text, re.IGNORECASE)
        if match:
            return match.group(1)
    return None


def parse_legislation_html(html_path: Path, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Parse a legislation HTML file and extract structured content."""
    print(f"  Parsing: {html_path.name}")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'lxml')
    
    output = {
        "metadata": {
            **metadata,
            "parsed_at": datetime.now().isoformat(),
            "source_file": html_path.name
        },
        "sections": [],
        "definitions": []
    }
    
    # Find all section elements - legislation.govt.nz uses 'prov' class
    sections = soup.find_all('div', class_=re.compile(r'prov'))
    
    if not sections:
        # Fallback: try finding by heading structure
        sections = soup.find_all(['section', 'div'], class_=re.compile(r'section|provision'))
    
    print(f"    Found {len(sections)} provision elements")
    
    current_part = ""
    current_subpart = ""
    
    for section in sections:
        try:
            # Get section ID for URL linking
            section_id = section.get('id', '')
            
            # Find the section heading
            heading_elem = section.find(class_=re.compile(r'prov-heading|heading'))
            if not heading_elem:
                heading_elem = section.find(['h1', 'h2', 'h3', 'h4', 'h5'])
            
            heading = clean_text(heading_elem.get_text()) if heading_elem else ""
            
            # Find section number
            num_elem = section.find(class_=re.compile(r'prov-num|section-num'))
            section_num = clean_text(num_elem.get_text()) if num_elem else ""
            if not section_num:
                section_num = extract_section_number(heading) or ""
            
            # Get the body text
            body_elem = section.find(class_=re.compile(r'prov-body|section-body'))
            if body_elem:
                body_text = clean_text(body_elem.get_text())
            else:
                # Get all text minus the heading
                body_text = clean_text(section.get_text())
                if heading:
                    body_text = body_text.replace(heading, '', 1).strip()
            
            if not body_text and not heading:
                continue
            
            # Determine level
            level = "section"
            if re.match(r'^Part\s+\d+', heading, re.IGNORECASE):
                level = "part"
                current_part = heading
            elif re.match(r'^Subpart\s+', heading, re.IGNORECASE):
                level = "subpart"
                current_subpart = heading
            elif re.match(r'^Schedule', heading, re.IGNORECASE):
                level = "schedule"
            
            # Build section URL
            section_url = metadata.get("url", "")
            if section_id:
                section_url = f"{metadata['url'].replace('/whole.html', '')}/DLM{section_id}" if 'DLM' not in section_id else f"{metadata['url'].replace('/whole.html', '')}/{section_id}"
            
            output["sections"].append({
                "section_number": section_num,
                "heading": heading,
                "level": level,
                "part": current_part,
                "subpart": current_subpart,
                "text": body_text[:5000],  # Limit text length
                "url": section_url,
                "act_title": metadata.get("title", ""),
                "act_short_name": metadata.get("short_name", "")
            })
            
        except Exception as e:
            print(f"    Warning: Error parsing section: {e}")
            continue
    
    # If no sections found with prov class, try a simpler approach
    if not output["sections"]:
        print(f"    Using fallback text extraction...")
        output["sections"] = extract_by_text_patterns(soup, metadata)
    
    print(f"    Extracted {len(output['sections'])} sections")
    
    return output


def extract_by_text_patterns(soup: BeautifulSoup, metadata: Dict) -> List[Dict]:
    """Fallback: Extract sections by looking for numbered headings in text."""
    sections = []
    
    # Get the main content
    body = soup.find('body')
    if not body:
        return sections
    
    # Find all heading-like elements
    headings = body.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    for heading in headings:
        heading_text = clean_text(heading.get_text())
        
        # Check if this looks like a section heading
        if re.match(r'^\d+[A-Z]?\s+\w', heading_text):
            section_num = extract_section_number(heading_text) or ""
            
            # Get the next sibling content
            content_parts = []
            sibling = heading.find_next_sibling()
            while sibling and sibling.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                content_parts.append(clean_text(sibling.get_text()))
                sibling = sibling.find_next_sibling()
            
            body_text = ' '.join(content_parts)[:5000]
            
            if body_text:
                sections.append({
                    "section_number": section_num,
                    "heading": heading_text,
                    "level": "section",
                    "part": "",
                    "subpart": "",
                    "text": body_text,
                    "url": metadata.get("url", ""),
                    "act_title": metadata.get("title", ""),
                    "act_short_name": metadata.get("short_name", "")
                })
    
    return sections


def main():
    """Main entry point."""
    print("=" * 60)
    print("NZ Legislation Parser")
    print("=" * 60)
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find HTML files
    html_files = list(RAW_HTML_DIR.glob("*.html"))
    
    if not html_files:
        print(f"\nNo HTML files found in {RAW_HTML_DIR.absolute()}")
        print("Please download the legislation HTML files first.")
        return
    
    print(f"\nFound {len(html_files)} HTML files to process:\n")
    
    all_acts = []
    total_sections = 0
    
    for html_path in sorted(html_files):
        # Get metadata for this file
        metadata = ACT_METADATA.get(html_path.name, {
            "title": html_path.stem.replace("-", " ").title(),
            "year": 0,
            "number": 0,
            "url": "",
            "short_name": html_path.stem[:3].upper(),
            "topics": []
        })
        
        # Parse the HTML
        result = parse_legislation_html(html_path, metadata)
        all_acts.append(result)
        total_sections += len(result["sections"])
        
        # Save individual JSON file
        output_path = OUTPUT_DIR / f"{html_path.stem}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    # Save combined index
    index_path = OUTPUT_DIR / "acts_index.json"
    index_data = {
        "generated_at": datetime.now().isoformat(),
        "total_acts": len(all_acts),
        "total_sections": total_sections,
        "acts": [
            {
                "title": act["metadata"]["title"],
                "short_name": act["metadata"].get("short_name", ""),
                "year": act["metadata"].get("year", 0),
                "sections_count": len(act["sections"]),
                "file": f"{Path(act['metadata']['source_file']).stem}.json"
            }
            for act in all_acts
        ]
    }
    
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("PARSING COMPLETE!")
    print("=" * 60)
    print(f"Acts processed: {len(all_acts)}")
    print(f"Total sections: {total_sections}")
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    print(f"\nFiles created:")
    for act in all_acts:
        stem = Path(act['metadata']['source_file']).stem
        print(f"  - {stem}.json ({len(act['sections'])} sections)")
    print(f"  - acts_index.json")


if __name__ == "__main__":
    main()