"""
Output Writer Module
Handles writing results to JSON and TXT files.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .extractor import CandidateTerm
from .clusterer import ClusteringResult


def ensure_output_dir(output_dir: Path) -> None:
    """Create output directory if it doesn't exist."""
    output_dir.mkdir(parents=True, exist_ok=True)


def write_json(data: Any, filepath: Path) -> None:
    """Write data to JSON file with pretty formatting."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_txt(content: str, filepath: Path) -> None:
    """Write content to text file."""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


def write_raw_candidates(
    candidates: dict[str, CandidateTerm],
    output_dir: Path,
    num_source_files: int
) -> None:
    """
    Write raw candidates to output files (1_raw_candidates.json/.txt).
    """
    ensure_output_dir(output_dir)

    # Sort by count descending
    sorted_candidates = sorted(
        candidates.values(),
        key=lambda x: (len(x.sources), x.count),
        reverse=True
    )

    # Build JSON data
    json_data = {
        "metadata": {
            "total_extracted": len(candidates),
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
            "source_files": num_source_files
        },
        "candidates": [
            {
                "term": c.term,
                "count": c.count,
                "num_sources": len(c.sources),
                "sources": sorted(c.sources),
                "signals": sorted(c.signals),
                "original_forms": sorted(c.original_forms)
            }
            for c in sorted_candidates
        ]
    }

    write_json(json_data, output_dir / "1_raw_candidates.json")

    # Build TXT content
    txt_lines = [
        "RAW CANDIDATES EXTRACTED",
        "=" * 50,
        f"Total candidates extracted: {len(candidates)}",
        f"Source files processed: {num_source_files}",
        f"Extraction date: {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "CANDIDATES (sorted by frequency)",
        "-" * 50,
        ""
    ]

    for c in sorted_candidates:
        signals_str = ", ".join(sorted(c.signals))
        txt_lines.append(f"{c.term} ({c.count} occurrences, {len(c.sources)} sources)")
        txt_lines.append(f"  Signals: {signals_str}")
        txt_lines.append("")

    write_txt("\n".join(txt_lines), output_dir / "1_raw_candidates.txt")


def write_filtered_candidates(
    filtered: dict[str, CandidateTerm],
    removed: dict[str, CandidateTerm],
    output_dir: Path,
    min_occurrences: int
) -> None:
    """
    Write filtered candidates to output files (2_filtered_candidates.json/.txt).
    """
    ensure_output_dir(output_dir)

    # Sort by count descending
    sorted_filtered = sorted(
        filtered.values(),
        key=lambda x: (len(x.sources), x.count),
        reverse=True
    )

    # Build JSON data
    json_data = {
        "metadata": {
            "total_after_filtering": len(filtered),
            "total_removed": len(removed),
            "filtering_criteria": {
                "min_occurrences": min_occurrences,
                "removed_common_english": True,
                "removed_company_names": True,
                "removed_locations": True
            }
        },
        "candidates": [
            {
                "term": c.term,
                "count": c.count,
                "num_sources": len(c.sources),
                "sources": sorted(c.sources)
            }
            for c in sorted_filtered
        ]
    }

    write_json(json_data, output_dir / "2_filtered_candidates.json")

    # Build TXT content
    txt_lines = [
        "FILTERED CANDIDATES",
        "=" * 50,
        f"Total after filtering: {len(filtered)}",
        f"Total removed: {len(removed)}",
        f"Min occurrences threshold: {min_occurrences}",
        "",
        "CANDIDATES (sorted by frequency)",
        "-" * 50,
        ""
    ]

    for c in sorted_filtered:
        txt_lines.append(f"{c.term} ({c.count} occurrences, {len(c.sources)} sources)")

    write_txt("\n".join(txt_lines), output_dir / "2_filtered_candidates.txt")


def write_clustered_keywords(
    clustering_result: ClusteringResult,
    output_dir: Path
) -> None:
    """
    Write clustering results to output files (3_clustered_keywords.json/.txt).
    """
    ensure_output_dir(output_dir)

    # Build JSON data
    json_data = {
        "metadata": {
            "algorithm": clustering_result.algorithm,
            "num_clusters": clustering_result.num_clusters,
            "silhouette_score": clustering_result.silhouette_score,
            "unclusterable_count": len(clustering_result.unclusterable)
        },
        "clusters": [
            {
                "cluster_id": cluster.cluster_id,
                "suggested_label": cluster.suggested_label,
                "terms": cluster.terms,
                "centroid_nearest": cluster.centroid_nearest,
                "term_count": len(cluster.terms)
            }
            for cluster in clustering_result.clusters
        ],
        "unclusterable": sorted(clustering_result.unclusterable)
    }

    write_json(json_data, output_dir / "3_clustered_keywords.json")

    # Build TXT content
    txt_lines = [
        "CLUSTERED KEYWORDS",
        "=" * 50,
        f"Algorithm: {clustering_result.algorithm}",
        f"Number of clusters: {clustering_result.num_clusters}",
        f"Silhouette score: {clustering_result.silhouette_score}",
        f"Unclusterable terms: {len(clustering_result.unclusterable)}",
        "",
        "CLUSTERS",
        "-" * 50,
        ""
    ]

    for cluster in clustering_result.clusters:
        txt_lines.append(f"Cluster {cluster.cluster_id}: {cluster.suggested_label}")
        txt_lines.append(f"  Central term: {cluster.centroid_nearest}")
        txt_lines.append(f"  Terms ({len(cluster.terms)}):")
        for term in cluster.terms:
            txt_lines.append(f"    - {term}")
        txt_lines.append("")

    if clustering_result.unclusterable:
        txt_lines.append("")
        txt_lines.append("UNCLUSTERABLE TERMS (no valid embeddings)")
        txt_lines.append("-" * 50)
        for term in sorted(clustering_result.unclusterable):
            txt_lines.append(f"  - {term}")

    write_txt("\n".join(txt_lines), output_dir / "3_clustered_keywords.txt")


def write_manual_review_template(
    candidates: dict[str, CandidateTerm],
    output_dir: Path
) -> None:
    """
    Write manual review template (4_manual_review_template.json/.txt).
    """
    ensure_output_dir(output_dir)

    # Sort by count descending
    sorted_candidates = sorted(
        candidates.values(),
        key=lambda x: (len(x.sources), x.count),
        reverse=True
    )

    # Predefined categories
    categories = [
        "Programming Languages",
        "Frameworks/Libraries",
        "Databases",
        "Cloud/Infrastructure",
        "DevOps/Tools",
        "Methodologies/Practices",
        "Concepts/Domains",
        "Uncategorized"
    ]

    # Build JSON data
    json_data = {
        "instructions": "Assign each term to a category by filling in the 'category' field. Add new categories to the list as needed.",
        "categories": categories,
        "terms": [
            {
                "term": c.term,
                "count": c.count,
                "num_sources": len(c.sources),
                "category": ""
            }
            for c in sorted_candidates
        ]
    }

    write_json(json_data, output_dir / "4_manual_review_template.json")

    # Build TXT content
    txt_lines = [
        "MANUAL REVIEW TEMPLATE",
        "=" * 50,
        "",
        "Instructions:",
        "Assign each term below to one of the categories.",
        "Add new categories as needed.",
        "",
        "Categories:",
    ]
    for cat in categories:
        txt_lines.append(f"  - {cat}")

    txt_lines.extend([
        "",
        "TERMS TO CATEGORIZE",
        "-" * 50,
        "",
        "Format: TERM (count, sources) -> CATEGORY",
        ""
    ])

    for c in sorted_candidates:
        txt_lines.append(f"{c.term} ({c.count}, {len(c.sources)} sources) -> ")

    write_txt("\n".join(txt_lines), output_dir / "4_manual_review_template.txt")


def write_by_company(
    candidates: dict[str, CandidateTerm],
    output_dir: Path
) -> None:
    """
    Write terms grouped by company (5_by_company.json/.txt).
    """
    ensure_output_dir(output_dir)

    # Build company -> terms mapping
    company_terms: dict[str, set[str]] = {}

    for candidate in candidates.values():
        for company in candidate.sources:
            if company not in company_terms:
                company_terms[company] = set()
            company_terms[company].add(candidate.term)

    # Sort companies by term count
    sorted_companies = sorted(
        company_terms.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    # Build JSON data
    json_data = {
        company: {
            "all_terms": sorted(terms),
            "term_count": len(terms)
        }
        for company, terms in sorted_companies
    }

    write_json(json_data, output_dir / "5_by_company.json")

    # Build TXT content
    txt_lines = [
        "TERMS BY COMPANY",
        "=" * 50,
        f"Total companies: {len(company_terms)}",
        "",
        "COMPANIES (sorted by term count)",
        "-" * 50,
        ""
    ]

    for company, terms in sorted_companies:
        txt_lines.append(f"{company} ({len(terms)} terms)")
        for term in sorted(terms):
            txt_lines.append(f"  - {term}")
        txt_lines.append("")

    write_txt("\n".join(txt_lines), output_dir / "5_by_company.txt")


def write_summary_stats(
    candidates: dict[str, CandidateTerm],
    num_source_files: int,
    output_dir: Path
) -> None:
    """
    Write summary statistics (6_summary_stats.json/.txt).
    """
    ensure_output_dir(output_dir)

    # Sort by count
    sorted_candidates = sorted(
        candidates.values(),
        key=lambda x: (len(x.sources), x.count),
        reverse=True
    )

    # Top 20 terms
    top_20 = sorted_candidates[:20]

    # Frequency buckets
    buckets = {"50+": 0, "20-49": 0, "10-19": 0, "5-9": 0, "2-4": 0, "1": 0}
    for c in sorted_candidates:
        sources = len(c.sources)
        if sources >= 50:
            buckets["50+"] += 1
        elif sources >= 20:
            buckets["20-49"] += 1
        elif sources >= 10:
            buckets["10-19"] += 1
        elif sources >= 5:
            buckets["5-9"] += 1
        elif sources >= 2:
            buckets["2-4"] += 1
        else:
            buckets["1"] += 1

    # Companies with most terms
    company_term_counts: dict[str, int] = {}
    for c in sorted_candidates:
        for company in c.sources:
            company_term_counts[company] = company_term_counts.get(company, 0) + 1

    top_companies = sorted(
        company_term_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]

    # Build JSON data
    json_data = {
        "total_files_processed": num_source_files,
        "total_unique_terms": len(candidates),
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "top_20_terms": [
            {"term": c.term, "count": c.count, "num_sources": len(c.sources)}
            for c in top_20
        ],
        "terms_by_frequency_bucket": buckets,
        "companies_with_most_terms": [
            {"company": company, "term_count": count}
            for company, count in top_companies
        ]
    }

    write_json(json_data, output_dir / "6_summary_stats.json")

    # Build TXT content
    txt_lines = [
        "SUMMARY STATISTICS",
        "=" * 50,
        f"Files processed: {num_source_files}",
        f"Unique terms extracted: {len(candidates)}",
        f"Date: {datetime.now().strftime('%Y-%m-%d')}",
        "",
        "TOP 20 TERMS",
        "-" * 50,
    ]

    for i, c in enumerate(top_20, 1):
        txt_lines.append(f"  {i:2}. {c.term} ({c.count} occurrences, {len(c.sources)} sources)")

    txt_lines.extend([
        "",
        "TERMS BY FREQUENCY (number of sources)",
        "-" * 50,
    ])
    for bucket, count in buckets.items():
        txt_lines.append(f"  {bucket}: {count} terms")

    txt_lines.extend([
        "",
        "TOP 10 COMPANIES BY TERM COUNT",
        "-" * 50,
    ])
    for company, count in top_companies:
        txt_lines.append(f"  {company}: {count} terms")

    write_txt("\n".join(txt_lines), output_dir / "6_summary_stats.txt")
