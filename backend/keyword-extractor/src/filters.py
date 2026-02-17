"""
Filters Module
Handles noise filtering for candidate terms.
"""

import re
from typing import Set

from .extractor import CandidateTerm


# Common English words to filter out (top frequent words + job posting jargon)
COMMON_ENGLISH_STOPWORDS: Set[str] = {
    # Common words
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i",
    "it", "for", "not", "on", "with", "he", "as", "you", "do", "at",
    "this", "but", "his", "by", "from", "they", "we", "say", "her", "she",
    "or", "an", "will", "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which", "go", "me",
    "when", "make", "can", "like", "time", "no", "just", "him", "know", "take",
    "people", "into", "year", "your", "good", "some", "could", "them", "see", "other",
    "than", "then", "now", "look", "only", "come", "its", "over", "think", "also",
    "back", "after", "use", "two", "how", "our", "work", "first", "well", "way",
    "even", "new", "want", "because", "any", "these", "give", "day", "most", "us",
    "being", "been", "has", "had", "does", "did", "doing", "done", "such", "own",
    "same", "here", "more", "where", "while", "should", "each", "under", "need",
    "very", "through", "may", "during", "before", "between", "those", "per",

    # Job posting specific - expanded
    "experience", "team", "teams", "work", "working", "ability", "strong", "skills",
    "excellent", "required", "preferred", "years", "year", "including", "must",
    "responsibilities", "qualifications", "requirements", "benefits", "benefit",
    "opportunity", "opportunities", "environment", "role", "roles", "position", "company", "business",
    "looking", "seeking", "ideal", "candidate", "candidates", "successful", "join",
    "development", "building", "build", "create", "creating", "design", "designing", "develop", "developing",
    "support", "supporting", "ensure", "ensuring", "provide", "providing", "maintain", "maintaining",
    "manage", "managing", "lead", "leading", "collaborate", "collaborating",
    "communication", "problem", "solving", "technical", "technologies", "technology",
    "engineering", "software", "engineer", "engineers", "developer", "developers",
    "senior", "junior", "staff", "principal", "associate", "intern", "internship",
    "level", "based", "across", "within", "multiple", "various",
    "high", "quality", "best", "practices", "practice", "solutions", "solution", "systems", "system",
    "products", "product", "services", "service", "customers", "customer", "users", "user",
    "clients", "client", "partners", "partner", "stakeholders", "stakeholder",
    "cross", "functional", "drive", "driving", "impact", "scale", "scaling",
    "growth", "innovation", "innovative", "culture", "values", "diversity", "inclusion", "inclusive",
    "equal", "employment", "employer", "applicants", "applicant", "consideration",
    "status", "race", "color", "religion", "sex", "national", "origin", "ancestry",
    "disability", "veteran", "veterans", "protected", "characteristics", "characteristic", "law", "laws",
    "apply", "application", "applications", "process", "interview", "interviews", "offer", "offers",
    "salary", "salaries", "compensation", "equity", "bonus", "bonuses", "benefits", "insurance",
    "health", "healthcare", "dental", "vision", "retirement", "vacation", "paid", "time", "off",
    "remote", "hybrid", "office", "onsite", "on-site", "location", "locations", "relocation", "visa",
    "sponsorship", "authorization", "citizen", "citizens", "resident", "residents", "permanent",

    # Education terms (not tech-specific)
    "bachelor", "bachelors", "master", "masters", "degree", "degrees", "phd", "doctorate",
    "university", "college", "education", "educational", "graduate", "undergraduate",
    "science", "sciences", "computer science", "studies", "program", "programs",
    "certification", "certifications", "certified", "accredited",

    # Generic business/job terms
    "full", "part", "full-time", "part-time", "contract", "contractor", "temporary", "temp",
    "permanent", "regular", "hourly", "annual", "monthly", "weekly", "daily",
    "minimum", "maximum", "range", "ranges", "base", "total", "target", "competitive",
    "comprehensive", "extensive", "relevant", "related", "equivalent", "similar",
    "knowledge", "understanding", "familiarity", "familiar", "proficiency", "proficient",
    "expertise", "expert", "experts", "specialist", "specialists", "professional", "professionals",
    "passion", "passionate", "enthusiasm", "enthusiastic", "motivated", "self-motivated",
    "detail", "details", "detailed", "oriented", "orientation", "focused", "focus",
    "fast", "paced", "fast-paced", "dynamic", "challenging", "exciting", "rewarding",
    "collaborative", "collaboration", "independent", "independently", "autonomy", "autonomous",
    "learn", "learning", "learner", "teach", "teaching", "mentor", "mentoring", "coach", "coaching",
    "leader", "leadership", "ownership", "initiative", "initiatives", "proactive",
    "critical", "analytical", "analysis", "creative", "creativity", "innovative",
    "effective", "effectively", "efficient", "efficiently", "timely", "deadline", "deadlines",
    "project", "projects", "task", "tasks", "assignment", "assignments", "deliverable", "deliverables",
    "goal", "goals", "objective", "objectives", "outcome", "outcomes", "result", "results",
    "strategy", "strategies", "strategic", "tactical", "execution", "execute", "implement", "implementation",
    "plan", "planning", "roadmap", "milestone", "milestones", "timeline", "timelines",
    "performance", "performing", "perform", "achieve", "achieving", "achievement", "achievements",
    "improve", "improving", "improvement", "improvements", "optimize", "optimizing", "optimization",
    "review", "reviewing", "reviews", "feedback", "evaluate", "evaluating", "evaluation",
    "report", "reporting", "reports", "document", "documenting", "documentation",
    "meeting", "meetings", "presentation", "presentations", "present", "presenting",
    "write", "writing", "written", "verbal", "oral", "interpersonal",
    "organization", "organizational", "organizations", "industry", "industries",
    "market", "markets", "sector", "sectors", "field", "fields", "area", "areas", "domain", "domains",
    "internal", "external", "global", "local", "regional", "international", "domestic",
    "small", "medium", "large", "enterprise", "enterprises", "startup", "startups",
    "mission", "vision", "core", "key", "primary", "secondary", "main", "major", "minor",
    "current", "future", "existing", "potential", "possible", "available", "open",
    "help", "helping", "helps", "assist", "assisting", "assistance",
    "job", "jobs", "career", "careers", "employment", "hire", "hiring", "recruit", "recruiting",

    # Time-related
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december", "today", "week", "month",
    "quarter", "quarterly", "annual", "annually", "pm", "am",

    # Generic adjectives/adverbs
    "great", "good", "better", "best", "top", "excellent", "outstanding", "exceptional",
    "successful", "strong", "solid", "robust", "reliable", "flexible", "adaptable",
    "quick", "quickly", "rapid", "rapidly", "fast", "slow", "early", "late",
    "able", "capable", "competent", "skilled", "talented", "gifted",
    "right", "appropriate", "suitable", "fit", "ideal", "perfect",
    "real", "actual", "true", "correct", "accurate", "precise",
    "clear", "clearly", "complete", "completely", "full", "fully", "entire", "entirely",
    "specific", "specifically", "particular", "particularly", "especially", "general", "generally",

    # Numbers as words
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve", "hundred", "thousand", "million", "billion",

    # Misc
    "etc", "ie", "eg", "via", "per", "plus", "including", "included", "includes",
    "following", "follows", "follow", "regarding", "related", "relating",
    "information", "info", "details", "detail", "description", "descriptions",
    "note", "notes", "please", "thank", "thanks",

    # Generic words that appear in job postings but aren't tech terms
    "guide", "studio", "develops", "inside", "bio", "springs", "audio", "amazon",
    "lux", "equi", "cv", "cardio", "shell", "elastic", "worldwide",

    # LinkedIn UI/scraping noise
    "linkedin", "save", "show", "visit", "post", "posted", "content", "privately",
    "advertising", "recommendation", "recommended", "select", "language", "settings",
    "updates", "update", "guidelines", "guideline", "choices", "choice", "transparency",
    "insights", "insight", "premium", "seeker", "exclusive", "powered", "promoted",
    "verified", "sources", "source", "competitors", "competitor", "cover letter",
    "notified", "excludes", "exclude", "seniority", "match", "matches", "actively",
    "questions", "question", "company-wide", "bing", "set", "jan", "feb", "mar", "apr",
    "jun", "jul", "aug", "sep", "oct", "nov", "dec",
    "community", "communities", "privacy", "safety", "accessibility", "interested",
    "marketing", "sales", "sexual orientation", "gender identity", "computer", "york",
    "bay", "recommended content", "match details", "linkedin data", "cover letter",
    "verified job", "candidate seniority", "easy apply", "tailor", "put", "bring",
    "nice", "basic", "success", "life", "end", "participate", "contribute", "why",
    "expansion", "founding", "grad", "medical", "pto", "employee", "employees",
    "total employees", "marital status", "genetic information", "reasonable accommodations",
    "school alumni", "over 100 people", "significant", "significant growth",
    "long-term", "cutting-edge", "world-class", "real-world", "high-quality",
    "in-person", "in-office", "job-related", "are", "los", "alto", "angeles",
    "product managers", "cross-functional teams", "job post", "401", "401k", "401(k",
    "more set alert", "save use ai", "research", "management", "platform", "google",

    # More generic terms that appear frequently but aren't specific tech
    "problem-solving", "problem solving", "hands-on", "hands on", "end-to-end",
    "real-time", "real time", "ad", "ads", "advertising", "data",

    # Additional generic words that appear but aren't tech-specific
    "side-by-side", "sell-side", "client-side", "server-side", "enterprise-wide",
    "viral loops", "cutting-edge", "advanced", "modern", "robust", "thoughtful",
    "peer", "peers", "conduct", "participate", "contribute",
}

# Common location words (cities, states, countries) - expanded
LOCATION_WORDS: Set[str] = {
    # US States (full and abbreviations)
    "california", "ca", "texas", "tx", "new york", "ny", "florida", "fl",
    "illinois", "il", "washington", "wa", "massachusetts", "ma", "colorado", "co",
    "georgia", "ga", "virginia", "va", "north carolina", "nc", "south carolina", "sc",
    "arizona", "az", "oregon", "or", "pennsylvania", "pa", "ohio", "oh",
    "michigan", "mi", "new jersey", "nj", "maryland", "md", "tennessee", "tn",
    "indiana", "in", "minnesota", "mn", "wisconsin", "wi", "missouri", "mo",
    "connecticut", "ct", "utah", "ut", "nevada", "nv", "alabama", "al",
    "kentucky", "ky", "louisiana", "la", "oklahoma", "ok", "iowa", "ia",
    "arkansas", "ar", "kansas", "ks", "mississippi", "ms", "nebraska", "ne",
    "idaho", "id", "hawaii", "hi", "maine", "me", "montana", "mt",
    "new hampshire", "nh", "rhode island", "ri", "delaware", "de",
    "south dakota", "sd", "north dakota", "nd", "alaska", "ak", "vermont", "vt",
    "west virginia", "wv", "wyoming", "wy", "district of columbia", "dc",

    # Major US cities and fragments
    "san francisco", "san", "francisco", "new york city", "nyc", "los angeles", "la",
    "seattle", "austin", "denver", "boston", "chicago", "atlanta", "dallas",
    "houston", "miami", "phoenix", "portland", "san diego", "san jose",
    "palo alto", "mountain view", "sunnyvale", "menlo park", "cupertino",
    "redwood city", "santa clara", "fremont", "oakland", "berkeley",
    "irvine", "pasadena", "burbank", "glendale", "long beach", "anaheim",
    "sacramento", "fresno", "san bernardino", "riverside", "stockton",
    "bellevue", "redmond", "kirkland", "tacoma", "spokane",
    "boulder", "aurora", "colorado springs", "fort collins",
    "cambridge", "somerville", "worcester", "springfield",
    "brooklyn", "manhattan", "queens", "bronx", "staten island", "jersey city",
    "newark", "hoboken", "stamford", "white plains",
    "philadelphia", "pittsburgh", "baltimore", "arlington", "alexandria",
    "reston", "tysons", "mclean", "fairfax", "richmond", "norfolk",
    "charlotte", "raleigh", "durham", "chapel hill", "greensboro", "winston-salem",
    "nashville", "memphis", "knoxville", "chattanooga",
    "detroit", "ann arbor", "grand rapids", "lansing",
    "minneapolis", "st paul", "saint paul",
    "milwaukee", "madison", "green bay",
    "indianapolis", "fort wayne", "bloomington",
    "columbus", "cleveland", "cincinnati", "toledo", "akron",
    "kansas city", "st louis", "saint louis", "springfield",
    "salt lake city", "provo", "ogden",
    "las vegas", "reno", "henderson",
    "tempe", "scottsdale", "mesa", "chandler", "gilbert", "tucson",
    "albuquerque", "santa fe",
    "omaha", "lincoln",
    "des moines", "cedar rapids",
    "louisville", "lexington",
    "new orleans", "baton rouge",
    "birmingham", "huntsville", "montgomery",
    "tampa", "orlando", "jacksonville", "fort lauderdale", "west palm beach",

    # International cities
    "london", "paris", "berlin", "munich", "frankfurt", "amsterdam", "dublin",
    "zurich", "geneva", "stockholm", "copenhagen", "oslo", "helsinki",
    "madrid", "barcelona", "lisbon", "rome", "milan", "vienna", "prague",
    "warsaw", "budapest", "brussels", "luxembourg",
    "toronto", "vancouver", "montreal", "calgary", "ottawa", "waterloo",
    "sydney", "melbourne", "brisbane", "perth", "auckland", "wellington",
    "tokyo", "osaka", "kyoto", "singapore", "hong kong", "seoul", "taipei",
    "beijing", "shanghai", "shenzhen", "guangzhou", "hangzhou",
    "mumbai", "bangalore", "bengaluru", "hyderabad", "delhi", "pune", "chennai",
    "tel aviv", "jerusalem", "haifa",
    "dubai", "abu dhabi", "doha", "riyadh",
    "sao paulo", "rio de janeiro", "mexico city", "guadalajara", "monterrey",

    # Countries
    "united states", "usa", "us", "america", "american", "americas",
    "canada", "canadian", "uk", "united kingdom", "britain", "british", "england",
    "germany", "german", "france", "french", "spain", "spanish", "italy", "italian",
    "netherlands", "dutch", "belgium", "swiss", "switzerland", "austria", "austrian",
    "sweden", "swedish", "norway", "norwegian", "denmark", "danish", "finland", "finnish",
    "ireland", "irish", "scotland", "scottish", "wales", "welsh",
    "poland", "polish", "czech", "hungary", "hungarian", "romania", "romanian",
    "portugal", "portuguese", "greece", "greek", "turkey", "turkish",
    "russia", "russian", "ukraine", "ukrainian",
    "china", "chinese", "japan", "japanese", "korea", "korean", "south korea",
    "india", "indian", "singapore", "singaporean", "malaysia", "malaysian",
    "indonesia", "indonesian", "thailand", "thai", "vietnam", "vietnamese",
    "philippines", "filipino", "taiwan", "taiwanese", "hong kong",
    "australia", "australian", "new zealand",
    "israel", "israeli", "uae", "emirates", "saudi", "qatar",
    "brazil", "brazilian", "mexico", "mexican", "argentina", "argentinian",
    "chile", "chilean", "colombia", "colombian", "peru", "peruvian",
    "south africa", "nigeria", "kenya", "egypt",

    # Regions
    "bay area", "silicon valley", "tri-state", "midwest", "northeast", "southeast",
    "southwest", "pacific northwest", "east coast", "west coast", "gulf coast",
    "europe", "european", "asia", "asian", "africa", "african", "middle east",
    "latin america", "north america", "south america", "oceania", "apac", "emea", "latam",

    # Generic location terms
    "united", "states", "city", "county", "state", "country", "region", "area",
    "metro", "metropolitan", "greater", "downtown", "midtown", "uptown",
    "north", "south", "east", "west", "central", "northern", "southern", "eastern", "western",
}

# Words that are valid tech terms despite being short or common-looking
PROTECTED_TERMS: Set[str] = {
    # Languages (including short ones)
    "go", "r", "c", "d", "f#", "c++", "c#", "java", "python", "javascript", "typescript",
    "ruby", "rust", "swift", "kotlin", "scala", "php", "perl", "lua", "julia",
    "haskell", "erlang", "elixir", "clojure", "groovy", "dart", "objective-c",
    "fortran", "cobol", "lisp", "scheme", "ocaml", "f#", "vb", "vba",
    "bash", "shell", "powershell", "zsh", "awk", "sed",
    "sql", "plsql", "tsql", "nosql", "graphql", "sparql",
    "html", "css", "sass", "scss", "less", "xml", "json", "yaml", "toml",
    "markdown", "latex", "jsx", "tsx",

    # Short tech acronyms
    ".net", "ai", "ml", "ui", "ux", "ci", "cd", "db", "api", "sdk", "ide",
    "aws", "gcp", "aks", "eks", "gke", "k8s", "vm", "os",
    "ios", "js", "ts", "py", "rb",
    "qa", "it", "ip", "tcp", "udp", "http", "https", "ftp", "sftp", "smtp",
    "ssh", "ssl", "tls", "dns", "cdn", "vpn", "vpc", "lan", "wan",
    "iam", "sso", "mfa", "jwt", "oauth", "saml", "ldap", "ad",
    "s3", "ec2", "rds", "sqs", "sns", "ecs", "eks", "emr", "ecr",
    "gcs", "bq", "gcf", "gce", "gae",
    "npm", "pip", "gem", "mvn", "gradle", "maven", "yarn", "pnpm",
    "xml", "csv", "pdf", "svg", "png", "gif", "jpeg", "jpg",
    "gpu", "cpu", "ram", "ssd", "hdd", "nvme",
    "iot", "ar", "vr", "xr", "nlp", "cv", "dl", "rl", "nn",
    "gan", "rnn", "cnn", "lstm", "bert", "gpt", "llm", "rag", "lora",
    "etl", "elt", "olap", "oltp", "dbt", "dag",
    "hdfs", "hive", "hbase",
    "git", "svn", "ci/cd", "devsecops",
    "rest", "soap", "rpc", "grpc", "websocket", "mqtt", "amqp",
    "orm", "jpa", "jdbc", "odbc",
    "mvc", "mvvm", "spa", "pwa", "ssr", "csr",
    "dom", "html5", "css3", "es6", "es2015",
    "tdd", "bdd", "ddd", "oop", "fp", "aop",
    "saas", "paas", "iaas", "faas", "baas",
    "b2b", "b2c",
}


def is_noise_pattern(term: str) -> bool:
    """Check if term matches common noise patterns from web scraping."""
    term_stripped = term.strip()
    term_lower = term_stripped.lower()

    # Contains "linkedin" anywhere
    if "linkedin" in term_lower:
        return True

    # Contains "+X years" or "+X employees" or "+X benefit" or similar patterns
    if re.search(r"\+\s*\d*\s*(years?|employees?|benefits?|more|stock|bonus|developers?|engineers?|people|partners?)", term_lower):
        return True

    # Contains statistics patterns (100+ companies, 65M+ customers, etc.)
    if re.search(r"\d+\+?\s*(companies|customers|users|countries|firms|exchanges|outlets|subjects|lines|languages|days|weeks|months|insurers|minds|providers|litigations|events)", term_lower):
        return True

    # Contains "sec.gov" or hiring patterns
    if "sec.gov" in term_lower or "hiring" in term_lower:
        return True

    # Job title + company name patterns (Software Engineer RemoteHunter, etc.)
    job_title_words = ["software", "engineer", "developer", "devops", "ios", "machine", "learning", "data"]
    words_in_term = term_lower.split()
    if any(w in words_in_term for w in job_title_words):
        if len(words_in_term) >= 3 and re.search(r"[A-Z][a-z]+(?:[A-Z][a-z]+)+", term_stripped):
            return True
        # Also catch "iOS Developer crtd labs" style
        if re.search(r"(?:developer|engineer)\s+[a-z]+\s+[a-z]+", term_lower):
            return True

    # YC batch codes (YC S25, YC F25, YC W24, YC X25)
    if re.match(r"^YC\s+[SFWX]\d{2}$", term_stripped, re.IGNORECASE):
        return True

    # Job reference IDs (letter + numbers like R277297, A3061877, J0825, etc.)
    if re.match(r"^[A-Z]{1,3}\d{3,}$", term_stripped):
        return True

    # Level/IC codes (IC1, IC2, L2, L3, L4, NC2, VS2, etc.)
    if re.match(r"^[A-Z]{1,2}\d{1,2}$", term_stripped) and term_lower not in PROTECTED_TERMS:
        return True

    # Batch/quarter codes (S25, F25, W24, Q1, Q4, H1, etc.) - but not tech terms
    if re.match(r"^[SFWQH]\d{1,2}$", term_stripped) and term_lower not in PROTECTED_TERMS:
        return True

    # Malformed text with 'n' joining words (scraping artifacts)
    if re.search(r"[a-z]n[A-Z]|nn[A-Z]|n[A-Z][a-z]+$", term_stripped):
        return True

    # Malformed concatenations (integratingAI, orJira, likeAndroid, yearYour)
    # These are lowercase word + uppercase continuation without proper separation
    if re.match(r"^[a-z]+[A-Z][a-z]+", term_stripped) and len(term_stripped) > 6:
        # Check if first part is a common English word fragment
        first_part_match = re.match(r"^([a-z]+)[A-Z]", term_stripped)
        if first_part_match:
            first_part = first_part_match.group(1).lower()
            common_prefixes = ["integrating", "or", "like", "year", "processing", "source", "trust", "selling", "leverage", "schools", "build", "about", "why", "either"]
            if first_part in common_prefixes:
                return True

    # Unicode escape sequences
    if re.search(r"u003[e>]", term_lower):
        return True

    # Timestamps (10:23 PM, 12:00 AM, etc.)
    if re.match(r"^\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?$", term_stripped):
        return True

    # Salary patterns with K notation (100K, 150K-200K, K/yr, etc.)
    if re.search(r"\d+K(?:/yr|/hr)?|\$?\d+K\s*-\s*\$?\d+K|K/yr\s*-\s*K", term_stripped, re.IGNORECASE):
        return True

    # Salary patterns with yr/bonus
    if re.search(r"yr\s*\+\s*(stock|bonus)", term_lower):
        return True

    # Price patterns (.00 - .00)
    if re.search(r"\.00\s*-\s*\.00", term_stripped):
        return True

    # Employee count patterns (1001-5000 employees, 51-200, etc.)
    if re.search(r"\d+\s*-\s*\d+\s*employees", term_stripped, re.IGNORECASE):
        return True
    if re.match(r"^\d+-\d+\s*employees?$", term_stripped, re.IGNORECASE):
        return True

    # Pure numeric with units or ranges
    if re.match(r"^[\d,.\-\s]+(?:K|M|B|k|m|b|hr|yr|%|GB|MB|TB)?$", term_stripped):
        return True

    # Date/time patterns
    if re.match(r"^\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}$", term_stripped):
        return True
    if re.match(r"^\d{4}[-–]\d{4}$", term_stripped):
        return True

    # Year + word patterns (2026 Questions, etc.)
    if re.match(r"^\d{4}\s+\w+", term_stripped):
        return True

    # Starts with special characters or numbers followed by noise
    if re.match(r"^[#\-\(\)\"\'·]+\s*\d", term_stripped):
        return True

    # Starts with · (bullet point from scraping)
    if term_stripped.startswith("·"):
        return True

    # Parenthetical fragments
    if re.match(r"^\([^)]*$", term_stripped) or re.match(r"^[^(]*\)$", term_stripped):
        return True

    # Just punctuation and spaces
    if re.match(r"^[\s\-\.\,\;\:\!\?\(\)\[\]\{\}\"\'\/\\]+$", term_stripped):
        return True

    # Very long terms (likely sentence fragments)
    if len(term_stripped.split()) > 4:
        return True

    # Contains currency symbols with numbers
    if re.search(r"[\$€£¥]\s*[\d,]+", term_stripped):
        return True

    # URL-like fragments
    if re.search(r"\.com|\.org|\.net|\.io|\.ai|\.co|www\.|http", term_stripped, re.IGNORECASE):
        return True

    # Contains "USD" (salary info)
    if "usd" in term_lower:
        return True

    # Contains "ARR" or financial metrics
    if re.search(r"\d+[MBK]?\+?\s*ARR", term_stripped):
        return True

    # Random hex/alphanumeric strings (ff82, VpDDQfyzOf, etc.)
    if re.match(r"^[a-f0-9]{4,}$", term_lower):  # Hex strings
        return True
    if re.match(r"^[A-Za-z]{8,}$", term_stripped) and not any(c in term_lower for c in "aeiou"):
        # Long string with no vowels - likely garbage
        return True

    # Job metadata phrases
    job_metadata_patterns = [
        r"job\s*(#|openings?|post)",
        r"easy\s*apply",
        r"phd\s*(student|level|expertise)",
        r"dod\s*clearance",
        r"github\s*profile",
        r"why\s*join",
        r"is\s*valuable",
        r"co-?ops?",
        r"portfolio",
        r"worldwide",
        r"pride",
        r"comptia",
        r"benefits?\s*bonus",
        r"graduation",
        r"govcon",
    ]
    for pattern in job_metadata_patterns:
        if re.search(pattern, term_lower):
            return True

    # Location fragments (SoHo, SoCal, FiDi, SoMa, etc.)
    location_fragments = ["soho", "socal", "fidi", "soma", "antonio", "ontario", "san antonio"]
    if term_lower in location_fragments:
        return True

    # Company/product name + City patterns (NetJets Columbus, GumGum Santa Monica, etc.)
    if re.search(r"[A-Z][a-z]+(?:[A-Z][a-z]+)*\s+(?:Columbus|Pittsburgh|Minneapolis|Seattle|Monica|Webster|Ogden|Norwalk)", term_stripped):
        return True

    # State abbreviation + Company name patterns (IL BlackRock, etc.)
    if re.match(r"^[A-Z]{2}\s+[A-Z][a-z]+", term_stripped):
        return True

    # Language codes and locale patterns (common in LinkedIn scraped data)
    # (Arabic) বাংলা, (Finnish) Français, Japanese) 한국어, etc.
    if re.match(r"^\([A-Za-z]+\)\s+", term_stripped):
        return True
    if re.search(r"\)\s+[^\x00-\x7F]", term_stripped):  # ) followed by non-ASCII
        return True
    if re.match(r"^[A-Za-z]+\)\s+", term_stripped):  # Missing opening paren
        return True

    # Non-ASCII characters (foreign language text from language selectors)
    # Keep only if it's a known tech term or mostly ASCII
    non_ascii_count = sum(1 for c in term_stripped if ord(c) > 127)
    if non_ascii_count > len(term_stripped) * 0.3:  # More than 30% non-ASCII
        return True

    # Random scraped UI elements
    if re.search(r"/yr\s*-\s*/yr|/hr\s*-\s*/hr|\d+\.\d+K", term_stripped):
        return True

    # LinkedIn-specific UI patterns
    linkedin_noise_patterns = [
        r"select language",
        r"show\s+\w+\s+details",
        r"be notified",
        r"cover letter",
        r"linkedin data",
        r"verified job",
        r"candidate seniority",
        r"recommended content",
    ]
    for pattern in linkedin_noise_patterns:
        if re.search(pattern, term_lower):
            return True

    # Company name patterns - CamelCase names that end with typical company suffixes
    company_suffixes = ["Hub", "Lab", "Labs", "Point", "Solve", "Link", "Finder", "Tech", "Ware",
                        "Wise", "Soft", "Sure", "Wave", "View", "Meter", "Health", "Brain", "Heart",
                        "Works", "Stack", "Base", "Amp", "Curve", "Tier", "Lock", "Smith", "Flair",
                        "Bridge", "Cast", "Flow", "Fort", "Adapt", "Sort", "Spect", "Gear", "Well",
                        "Fire", "Pool", "Cube", "Grid", "Lens", "Box", "Book", "Hive", "Rise", "Track",
                        "Vest", "Quest", "Dash", "Craft", "Gum", "Hill", "Ray", "Hawk", "Fox", "Jet",
                        "Pallet", "Mail", "Pass", "Brik", "Data", "Gate", "Force", "Match", "Sight",
                        "Pro", "Ops", "Ai", "AI", "IQ", "AQ", "Me", "ABA", "Rx", "Med", "Dox"]
    for suffix in company_suffixes:
        if term_stripped.endswith(suffix) and len(term_stripped) > len(suffix) + 2:
            # Check if it looks like a company name (CamelCase)
            if re.match(r"^[A-Z][a-z]+[A-Z]", term_stripped):
                # But not if it's a known tech pattern
                if term_lower not in PROTECTED_TERMS:
                    return True

    # Company/product names with ® or TM symbols
    if re.search(r"[®™]", term_stripped):
        return True

    # Patterns like "About X", "Why X", "X's mission/values/purpose/focus"
    if re.match(r"^(About|Why|Join|Us)\s+[A-Z]", term_stripped):
        return True
    if re.search(r"'s\s+(mission|values|purpose|focus|efforts|strategy|cloud|products|customers|earliest)", term_lower):
        return True

    # "X customers", "X employees", "X reserves", "X instances" patterns
    if re.search(r"[A-Z][a-z]+\s+(customers|employees|reserves|instances|products|applications|teams)", term_stripped):
        return True

    # Random alphanumeric IDs (like VpDDQfyzOf, TCP_01)
    if re.match(r"^[A-Za-z]{2,}_\d{2}$", term_stripped):
        return True
    if re.match(r"^[A-Z][a-z][A-Z]{2,}[a-z]{2,}[A-Z][a-z]+$", term_stripped):  # VpDDQfyzOf pattern
        return True

    return False


def is_numeric_or_date(term: str) -> bool:
    """Check if term is purely numeric or looks like a date."""
    # Pure numbers (including with commas and decimals)
    if re.match(r"^[\d,.\-/\s]+$", term.strip()):
        return True
    # Year ranges
    if re.match(r"^\d{4}[-–]\d{4}$", term.strip()):
        return True
    # Dates
    if re.match(r"^\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}$", term.strip()):
        return True
    # Numbers with K/M/B suffix
    if re.match(r"^\d+[KMB]$", term.strip(), re.IGNORECASE):
        return True
    return False


def is_location(term: str) -> bool:
    """Check if term is a location name."""
    return term.lower().strip() in LOCATION_WORDS


def is_common_word(term: str) -> bool:
    """Check if term is a common English word or job posting jargon."""
    term_lower = term.lower().strip()

    # Check if protected
    if term_lower in PROTECTED_TERMS:
        return False

    # Check against stopwords
    if term_lower in COMMON_ENGLISH_STOPWORDS:
        return True

    # For multi-word phrases, check if ALL words are common/locations
    words = term_lower.split()
    if len(words) > 1:
        all_common = all(
            w in COMMON_ENGLISH_STOPWORDS or w in LOCATION_WORDS
            for w in words
        )
        if all_common:
            return True

    return False


def has_tech_pattern(term: str) -> bool:
    """Check if term has patterns typical of tech terms."""
    # CamelCase (but not just two capital letters)
    if re.search(r"[a-z][A-Z]", term) and len(term) > 3:
        return True
    # Contains programming-specific special chars
    if re.search(r"[+#]", term) and not term.startswith("#"):
        return True
    # .js, .py, .NET style
    if re.search(r"\.[a-zA-Z]{1,4}$", term) and not re.search(r"\.com|\.org|\.net|\.io", term, re.IGNORECASE):
        return True
    # Version numbers attached to names (Python3, ES6, HTML5)
    if re.search(r"[a-zA-Z]+\d+$", term) and len(term) <= 10:
        return True
    # ALL_CAPS with underscore (CI_CD, REST_API) - but reasonable length
    if re.match(r"^[A-Z][A-Z0-9_]{1,15}$", term) and "_" in term:
        return True
    return False


def is_likely_tech_term(term: str) -> bool:
    """
    Positively identify terms that are likely tech-related.
    This is more aggressive than just filtering noise - it actively
    looks for tech indicators.
    """
    term_lower = term.lower().strip()

    # Check if it's a protected/known tech term
    if term_lower in PROTECTED_TERMS:
        return True

    # Check for tech patterns
    if has_tech_pattern(term):
        return True

    # Known tech-related suffixes/prefixes
    tech_suffixes = [
        "js", "db", "sql", "api", "sdk", "cli", "gui", "ide", "ops",
        "ql", "ml", "ai", "io", "ui", "ux",
    ]
    tech_prefixes = [
        "apache", "google", "amazon", "microsoft", "aws", "azure",
        "react", "angular", "vue", "node", "spring", "django", "flask",
        "docker", "kube", "terraform", "ansible",
        "mongo", "postgres", "mysql", "redis", "elastic",
        "kafka", "spark", "hadoop", "airflow",
        "tensor", "torch", "keras",
    ]

    for suffix in tech_suffixes:
        if term_lower.endswith(suffix) and len(term) > len(suffix):
            return True

    for prefix in tech_prefixes:
        if term_lower.startswith(prefix):
            return True

    # Multi-word tech phrases
    tech_phrase_patterns = [
        r"machine\s+learning",
        r"deep\s+learning",
        r"neural\s+network",
        r"data\s+structure",
        r"distributed\s+system",
        r"version\s+control",
        r"object[- ]oriented",
        r"functional\s+programming",
        r"micro\s*service",
        r"event[- ]driven",
        r"test[- ]driven",
        r"continuous\s+(integration|delivery|deployment)",
        r"ci[/\s]*cd",
        r"rest\s*api",
        r"web\s+service",
        r"cloud\s+(native|computing)",
        r"container\s*ization",
        r"code\s+review",
    ]

    for pattern in tech_phrase_patterns:
        if re.search(pattern, term_lower):
            return True

    # Check for ALL_CAPS acronyms that are 2-5 chars (likely tech acronyms)
    if re.match(r"^[A-Z]{2,5}$", term) and term_lower in PROTECTED_TERMS:
        return True

    return False


def filter_candidates(
    candidates: dict[str, CandidateTerm],
    company_names: Set[str],
    min_occurrences: int = 2
) -> tuple[dict[str, CandidateTerm], dict[str, CandidateTerm]]:
    """
    Filter candidate terms to remove noise.

    Args:
        candidates: Dictionary of candidate terms
        company_names: Set of company names to filter out
        min_occurrences: Minimum number of sources to keep (default 2)

    Returns:
        Tuple of (filtered_candidates, removed_candidates)
    """
    filtered = {}
    removed = {}

    # Normalize company names for comparison
    company_names_lower = {name.lower().strip() for name in company_names}
    # Also add individual words from company names
    for name in company_names:
        for word in name.lower().split():
            if len(word) > 2:
                company_names_lower.add(word)

    for key, candidate in candidates.items():
        term = candidate.term
        term_lower = term.lower().strip()

        # Determine the best original form to use
        best_form = term
        if candidate.original_forms:
            # Prefer forms with tech patterns
            for form in candidate.original_forms:
                if has_tech_pattern(form):
                    best_form = form
                    break
            else:
                # Use the form with most uppercase letters as likely proper name
                best_form = max(candidate.original_forms,
                               key=lambda x: sum(1 for c in x if c.isupper()))

        candidate.term = best_form
        term = best_form
        term_lower = term.lower().strip()

        # Apply filters (order matters - check noise patterns first)
        remove_reason = None

        # Check for scraping noise patterns
        if is_noise_pattern(term):
            remove_reason = "noise_pattern"

        # Check if numeric/date
        elif is_numeric_or_date(term):
            remove_reason = "numeric_or_date"

        # Check if it's a company name
        elif term_lower in company_names_lower:
            remove_reason = "company_name"

        # Check if location
        elif is_location(term):
            remove_reason = "location"

        # Check if common word (unless protected or has tech pattern)
        elif is_common_word(term) and not has_tech_pattern(term) and term_lower not in PROTECTED_TERMS:
            remove_reason = "common_word"

        # Check minimum occurrences (sources, not raw count)
        elif len(candidate.sources) < min_occurrences:
            # Keep single-occurrence terms only if they have strong tech patterns AND are protected
            if term_lower in PROTECTED_TERMS:
                pass  # Keep protected terms even with low frequency
            elif has_tech_pattern(term) and len(term) <= 20:
                pass  # Keep tech-patterned terms if not too long
            else:
                remove_reason = "low_frequency"

        # Check term length
        elif len(term.strip()) < 2 and term_lower not in PROTECTED_TERMS:
            remove_reason = "too_short"

        # Check for terms that are too long (likely sentence fragments)
        elif len(term.strip()) > 50:
            remove_reason = "too_long"

        # Final check: must look like a tech term to be kept
        # This is more aggressive but focuses results on actual tech keywords
        elif not is_likely_tech_term(term):
            remove_reason = "not_tech_term"

        # Add to appropriate dict
        if remove_reason:
            removed[key] = candidate
        else:
            filtered[key] = candidate

    return filtered, removed
