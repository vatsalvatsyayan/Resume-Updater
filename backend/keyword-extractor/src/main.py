"""
Main Entry Point
Orchestrates the keyword extraction pipeline.
"""

import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
    # Add the parent directory to sys.path to allow relative imports
    file_path = Path(__file__).resolve()
    sys.path.append(str(file_path.parent.parent))
    __package__ = file_path.parent.name

from .file_reader import get_all_job_descriptions
from .preprocessor import preprocess_text
from .extractor import KeywordExtractor, merge_candidates
from .filters import filter_candidates
from .clusterer import TermClusterer
from .output_writer import (
    write_raw_candidates,
    write_filtered_candidates,
    write_clustered_keywords,
    write_manual_review_template,
    write_by_company,
    write_summary_stats,
)


def run_extraction(input_dir: str | Path, output_dir: str | Path, min_occurrences: int = 2) -> None:
    """
    Run the full keyword extraction pipeline.

    Args:
        input_dir: Directory containing job description .txt files
        output_dir: Directory to write output files
        min_occurrences: Minimum sources for a term to be kept (default 2)
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    print("=" * 60)
    print("KEYWORD EXTRACTION PIPELINE")
    print("=" * 60)
    print()

    # Step 1: Read job descriptions
    print("[1/6] Reading job descriptions...")
    job_descriptions = get_all_job_descriptions(input_path)
    print(f"      Loaded {len(job_descriptions)} files")

    # Collect company names for filtering
    company_names = {jd.company for jd in job_descriptions}
    print(f"      Found {len(company_names)} unique companies")
    print()

    # Step 2: Extract candidates from each document
    print("[2/6] Extracting candidate terms...")
    extractor = KeywordExtractor()
    all_candidates = []

    for i, jd in enumerate(job_descriptions, 1):
        if i % 20 == 0 or i == len(job_descriptions):
            print(f"      Processing {i}/{len(job_descriptions)}...")

        # Preprocess text
        cleaned_text = preprocess_text(jd.content)

        # Extract candidates
        candidates = extractor.extract_candidates(cleaned_text, jd.company)
        all_candidates.append(candidates)

    # Merge all candidates
    merged_candidates = merge_candidates(all_candidates)
    print(f"      Extracted {len(merged_candidates)} unique candidate terms")
    print()

    # Step 3: Write raw candidates
    print("[3/6] Writing raw candidates...")
    write_raw_candidates(merged_candidates, output_path, len(job_descriptions))
    print("      Wrote 1_raw_candidates.json/.txt")
    print()

    # Step 4: Filter candidates
    print("[4/6] Filtering candidates...")
    filtered, removed = filter_candidates(
        merged_candidates,
        company_names,
        min_occurrences=min_occurrences
    )
    print(f"      Kept {len(filtered)} terms, removed {len(removed)} terms")

    write_filtered_candidates(filtered, removed, output_path, min_occurrences)
    print("      Wrote 2_filtered_candidates.json/.txt")
    print()

    # Step 5: Cluster terms
    print("[5/6] Clustering terms...")
    clusterer = TermClusterer()
    clustering_result = clusterer.cluster_terms(filtered)
    print(f"      Created {clustering_result.num_clusters} clusters")
    print(f"      Silhouette score: {clustering_result.silhouette_score}")
    print(f"      Unclusterable terms: {len(clustering_result.unclusterable)}")

    write_clustered_keywords(clustering_result, output_path)
    print("      Wrote 3_clustered_keywords.json/.txt")
    print()

    # Step 6: Write remaining outputs
    print("[6/6] Writing final outputs...")

    write_manual_review_template(filtered, output_path)
    print("      Wrote 4_manual_review_template.json/.txt")

    write_by_company(filtered, output_path)
    print("      Wrote 5_by_company.json/.txt")

    write_summary_stats(filtered, len(job_descriptions), output_path)
    print("      Wrote 6_summary_stats.json/.txt")

    print()
    print("=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Output directory: {output_path.absolute()}")
    print()
    print("Files generated:")
    print("  1. 1_raw_candidates.json/.txt     - All extracted terms")
    print("  2. 2_filtered_candidates.json/.txt - After noise removal")
    print("  3. 3_clustered_keywords.json/.txt  - Auto-clustered terms")
    print("  4. 4_manual_review_template.json/.txt - For your categorization")
    print("  5. 5_by_company.json/.txt          - Terms by company")
    print("  6. 6_summary_stats.json/.txt       - Summary statistics")


def main():
    """CLI entry point."""
    # Default paths relative to this file's location
    base_dir = Path(__file__).parent.parent
    default_input = base_dir / "job descriptions"
    default_output = base_dir / "output"

    # Allow command line overrides
    if len(sys.argv) >= 2:
        input_dir = Path(sys.argv[1])
    else:
        input_dir = default_input

    if len(sys.argv) >= 3:
        output_dir = Path(sys.argv[2])
    else:
        output_dir = default_output

    run_extraction(input_dir, output_dir)


if __name__ == "__main__":
    main()
