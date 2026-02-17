
import json
import re
from pathlib import Path

def clean_keywords(input_file: Path, output_file: Path):
    """
    Reads a text file of keyword candidates, filters out noise,
    and writes a clean JSON dictionary. Normalization is skipped.
    """
    print(f"Reading candidates from: {input_file}")
    with open(input_file, 'r') as f:
        lines = f.readlines()

    candidate_regex = re.compile(r"^(.*?)\s*\(\d+ occurrences, \d+ sources\)")

    raw_keywords = []
    for line in lines:
        match = candidate_regex.match(line)
        if match:
            raw_keywords.append(match.group(1).strip())

    print(f"Extracted {len(raw_keywords)} raw keywords.")

    # --- Filtering ---

    # Blocklist for noise, company names, non-tech terms, and ambiguous acronyms
    # Keeping case sensitivity for now to avoid merging, but blocklist is lowercase
    blocklist = {
        "ad", "it", "os", "ts", "qa", "ux", "ui", "go", "ai",
        "b2b", "saas", "ecommerce", "b2c",
        "phd-level", "remotehunter", "ridecontroller", "leapxpert", "metlife",
        "frostlocker", "capcenter", "golfforever", "myfundedfutures", "truecode",
        "techcrunch", "liveramp", "seatgeek", "nerdwallet", "worldcoin", "foxg1",
        "time100", "semianalysis", "iaxaI",
        "code reviews", "peer code reviews", "conduct code reviews", "thoughtful code reviews",
        "no use ai", "use ai",
        # Company names spotted in the list
        "remhunter", "ridecontroller", "leapxpert", "metlife", "frostlocker",
        "capcenter", "golfforever", "myfundedfutures", "truecode", "techcrunch",
        "liveramp", "spark capital", "seatgeek", "nerdwallet", "viegure",
        "mywellatdell", "workhelio", "meeboss", "sigma360", "sofi", "stackadapter",
        "shipbob", "truecar", "liveperson", "uipath", "bookwithmatrix", "leaderfactor",
        "ivorycloud", "smartmark", "truneighbor", "venturebeat", "duckduckgo",
        "biomerieux", "ebay inc.", "itradenetwork"
    }

    # --- Final Processing ---

    # Apply blocklist (case-insensitive) and remove duplicates
    # We keep the original casing from the file
    seen_keywords = set()
    cleaned_keywords = []
    for kw in raw_keywords:
        if kw.lower() not in blocklist and kw.lower() not in seen_keywords:
            cleaned_keywords.append(kw)
            seen_keywords.add(kw.lower())


    print(f"Kept {len(cleaned_keywords)} keywords after cleaning and de-duplication.")

    output_data = {
        "description": "A cleaned dictionary of technical keywords extracted from job descriptions. Noise has been filtered, but keywords have not been normalized.",
        "count": len(cleaned_keywords),
        "keywords": sorted(cleaned_keywords, key=str.lower)
    }

    print(f"Writing cleaned dictionary to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print("Cleaning complete.")

def main():
    """CLI entry point."""
    base_dir = Path(__file__).parent.parent
    input_file = base_dir / "output" / "2_filtered_candidates.txt"
    output_file = base_dir / "output" / "7_cleaned_tech_dictionary.json"

    if not input_file.exists():
        print(f"Error: Input file not found at {input_file}")
        return

    clean_keywords(input_file, output_file)


if __name__ == "__main__":
    main()
