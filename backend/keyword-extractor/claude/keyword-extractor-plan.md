# Keyword Extraction Project Plan

## Overview

Extract and categorize tech-related keywords from ~100+ job description files in `keyword-extractor/job descriptions/`. The goal is **discovery** - learning what tech terms appear across job postings, not just confirming known terms.

---

## 1. Input Handling

**Location:** `job descriptions/*.txt`

**Approach:**
- Use `pathlib.Path` for cross-platform path handling
- Read all `.txt` files from the input directory
- Extract company name from filename pattern: `{Company}_job_description.txt`
- Store metadata (filename, company) alongside content for per-company analysis

**Considerations:**
- Handle encoding issues (UTF-8 with fallback)
- Skip non-txt files if any exist
- Log files that fail to read

---

## 2. Text Extraction & Preprocessing

**Pipeline:**
1. **Normalize unicode** - Handle special characters (e.g., "Körber" in the data)
2. **Lowercase** - For matching, but preserve original case for output
3. **Remove URLs** - Job descriptions contain many links (careers pages, benefits)
4. **Remove email addresses** - Not relevant keywords
5. **Normalize whitespace** - Collapse multiple spaces/newlines

**What NOT to do:**
- Don't remove punctuation blindly (C++, .NET, Node.js need it)
- Don't stem/lemmatize (loses distinction between React vs ReactJS)

---

## 3. Keyword Extraction Strategy (Discovery-First)

### Step 1: Candidate Extraction

Use multiple signals to identify *potential* tech keywords:

**Signal A: Capitalization Patterns**
- `CamelCase` words → likely tech (PostgreSQL, JavaScript, GraphQL)
- `ALL_CAPS` with underscores → likely tech/config (REST_API, CI_CD)
- Mixed case in mid-sentence → proper nouns, often tech

**Signal B: Noun Phrase Extraction (spaCy)**
- Extract all noun phrases: "distributed systems", "machine learning", "version control"
- Captures multi-word concepts

**Signal C: Pattern Matching for Tech-Like Terms**
- Terms with dots: `Node.js`, `.NET`, `S3.amazonaws`
- Terms with plus/hash: `C++`, `C#`
- Terms with numbers: `Python3`, `H2O`, `OAuth2`
- Hyphenated compounds: `CI-CD`, `real-time`, `back-end`

**Signal D: Contextual Clues**
- Words appearing after "experience with", "proficiency in", "knowledge of", "familiar with"
- Words near other tech-like terms (clustering)

**Signal E: Statistical Signals**
- Terms that appear in multiple JDs but aren't generic English
- Filter out common English using word frequency lists

### Step 2: Noise Filtering

**Automatic Filters:**
- Remove pure numbers, dates, salary figures
- Remove company names (extracted from filenames)
- Remove location names (cities, states)
- Remove common business words (stopword list for job postings)
- Remove single characters (except `C`, `R`, `Go` with context)

**Frequency Threshold:**
- **Keep:** Terms appearing in 2+ JDs
- **Flag for review:** Single-occurrence terms with strong tech patterns
- **Discard:** Single-occurrence terms without tech patterns

### Step 3: Categorization (Two Parallel Approaches)

**Approach A: Manual Review**
- Output filtered candidates as JSON template
- User manually assigns categories
- Most accurate, full control

**Approach B: Clustering (Automated)**
- Use word embeddings (spaCy vectors)
- Cluster similar terms using k-means
- Output clusters with suggested labels based on cluster contents
- User reviews cluster assignments and names them

Both approaches run independently for comparison.

---

## 4. Output Structure

```
output/
├── 1_raw_candidates.txt
├── 1_raw_candidates.json
├── 2_filtered_candidates.txt
├── 2_filtered_candidates.json
├── 3_clustered_keywords.txt
├── 3_clustered_keywords.json
├── 4_manual_review_template.txt
├── 4_manual_review_template.json
├── 5_by_company.txt
├── 5_by_company.json
├── 6_summary_stats.txt
└── 6_summary_stats.json
```

### Output File Formats

**1_raw_candidates.json**
```json
{
  "metadata": {
    "total_extracted": 2847,
    "extraction_date": "2026-02-02",
    "source_files": 100
  },
  "candidates": [
    {"term": "Python", "count": 89, "sources": ["Microsoft", "Uber", ...]},
    {"term": "distributed systems", "count": 23, "sources": [...]},
    ...
  ]
}
```

**2_filtered_candidates.json**
```json
{
  "metadata": {
    "total_after_filtering": 487,
    "filtering_criteria": {
      "min_occurrences": 2,
      "removed_common_english": true,
      "removed_company_names": true
    }
  },
  "candidates": [
    {"term": "Python", "count": 89},
    {"term": "Kubernetes", "count": 45},
    ...
  ]
}
```

**3_clustered_keywords.json**
```json
{
  "metadata": {
    "algorithm": "k-means",
    "num_clusters": 8,
    "silhouette_score": 0.42
  },
  "clusters": [
    {
      "cluster_id": 0,
      "suggested_label": "Programming Languages",
      "terms": ["Python", "Java", "Go", "C++", "JavaScript", "TypeScript"],
      "centroid_nearest": "Java"
    },
    {
      "cluster_id": 1,
      "suggested_label": "Cloud/Infrastructure",
      "terms": ["AWS", "Kubernetes", "Docker", "Terraform", "GCP", "Azure"],
      "centroid_nearest": "AWS"
    },
    ...
  ]
}
```

**4_manual_review_template.json**
```json
{
  "instructions": "Assign each term to a category. Add new categories as needed.",
  "categories": [
    "Programming Languages",
    "Frameworks/Libraries",
    "Databases",
    "Cloud/Infrastructure",
    "DevOps/Tools",
    "Methodologies/Practices",
    "Concepts/Domains",
    "Uncategorized"
  ],
  "terms": [
    {"term": "Python", "count": 89, "category": ""},
    {"term": "Kubernetes", "count": 45, "category": ""},
    ...
  ]
}
```

**5_by_company.json**
```json
{
  "Microsoft": {
    "all_terms": ["C", "C++", "C#", "Java", "JavaScript", "Python"],
    "term_count": 6
  },
  "Uber": {
    "all_terms": ["Java", "Go", "Kubernetes", "distributed systems"],
    "term_count": 4
  },
  ...
}
```

**6_summary_stats.json**
```json
{
  "total_files_processed": 100,
  "total_unique_terms": 487,
  "top_20_terms": [
    {"term": "Python", "count": 89},
    {"term": "Java", "count": 76},
    ...
  ],
  "terms_by_frequency_bucket": {
    "50+": 5,
    "20-49": 23,
    "10-19": 45,
    "5-9": 87,
    "2-4": 327
  },
  "companies_with_most_terms": [
    {"company": "Datadog", "term_count": 12},
    ...
  ]
}
```

---

## 5. Project Structure

```
keyword-extractor/
├── job descriptions/           # Input (existing)
│   └── *.txt
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point / CLI
│   ├── file_reader.py          # Input handling
│   ├── preprocessor.py         # Text cleaning
│   ├── extractor.py            # Candidate extraction (all signals)
│   ├── filters.py              # Noise filtering logic
│   ├── clusterer.py            # Embedding + clustering logic
│   └── output_writer.py        # JSON/TXT generation
├── output/                     # Generated results (created on run)
│   └── (files listed above)
├── claude/                     # Planning docs
│   └── keyword-extractor-plan.md
├── requirements.txt
└── copy_helper.py              # (existing)
```

---

## 6. Dependencies

**requirements.txt:**
```
spacy>=3.7.0              # NLP: noun phrases, vectors
scikit-learn>=1.4.0       # Clustering (k-means)
numpy>=1.26.0             # Array operations for clustering
```

**Post-install:**
```bash
python -m spacy download en_core_web_md   # Medium model (has word vectors, ~40MB)
```

---

## 7. Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  INPUT: job descriptions/*.txt                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  EXTRACT: Capitalization, noun phrases, patterns, context   │
│  OUTPUT: 1_raw_candidates.json/.txt                         │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  FILTER: Remove noise, apply frequency threshold            │
│  OUTPUT: 2_filtered_candidates.json/.txt                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  CLUSTER         │    │  MANUAL TEMPLATE │
│  (automated)     │    │  (for user)      │
│                  │    │                  │
│  OUTPUT:         │    │  OUTPUT:         │
│  3_clustered_*   │    │  4_manual_*      │
└────────┬─────────┘    └────────┬─────────┘
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  AGGREGATE: Map terms to companies, compute stats           │
│  OUTPUT: 5_by_company.json/.txt, 6_summary_stats.json/.txt  │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Clustering Details

**Algorithm:** k-means (fast, interpretable)

**Determining k:** Elbow method or silhouette score

**Suggested label generation:**
- Look at terms in each cluster
- If cluster contains known anchor terms (Python, Java → "Programming Languages"), use that
- Otherwise, use the term closest to centroid as cluster name

**Handling terms without vectors:**
- Some tech terms may not have embeddings in spaCy (niche tools)
- These go into a separate "unclusterable" group for manual review

---

## 9. Potential Challenges & Mitigations

| Challenge | Mitigation |
|-----------|------------|
| **Tech terms with special chars** (`C++`, `.NET`, `Node.js`) | Regex patterns with escaped chars |
| **Acronyms vs words** (`Go` language vs "go to") | Context-aware matching; require word boundaries |
| **Version numbers** (`Python 3.x`, `Java 11`) | Normalize to base term |
| **Aliases** (`PostgreSQL/Postgres`, `K8s/Kubernetes`) | Surface both; user normalizes during review |
| **Multi-word terms** (`machine learning`, `Apache Spark`) | spaCy noun phrases handle these |
| **False positives** (`Oracle` company vs Oracle DB) | Context from JD; user decides during review |
| **Missing from embeddings** | Separate "unclusterable" group |
| **Encoding issues** (Körber) | UTF-8 handling with error fallback |
| **Empty/corrupt files** | Try/except with logging |
