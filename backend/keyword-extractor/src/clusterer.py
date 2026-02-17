"""
Clusterer Module
Handles term clustering using word embeddings.
"""

from dataclasses import dataclass
from typing import Optional

import numpy as np
import spacy
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from .extractor import CandidateTerm


@dataclass
class Cluster:
    """Represents a cluster of related terms."""
    cluster_id: int
    terms: list[str]
    suggested_label: str
    centroid_nearest: str  # Term closest to cluster centroid


@dataclass
class ClusteringResult:
    """Result of clustering operation."""
    clusters: list[Cluster]
    unclusterable: list[str]  # Terms without valid embeddings
    num_clusters: int
    silhouette_score: float
    algorithm: str = "k-means"


# Known anchor terms for suggesting cluster labels
ANCHOR_TERMS = {
    "programming_languages": ["python", "java", "javascript", "typescript", "go", "rust",
                              "c++", "c#", "ruby", "swift", "kotlin", "scala", "php"],
    "frameworks_libraries": ["react", "angular", "vue", "django", "flask", "spring",
                            "express", "rails", "fastapi", "nextjs", "nodejs"],
    "databases": ["postgresql", "mysql", "mongodb", "redis", "elasticsearch",
                  "dynamodb", "cassandra", "sqlite", "oracle", "sql server"],
    "cloud_infrastructure": ["aws", "gcp", "azure", "kubernetes", "docker", "terraform",
                             "ansible", "cloudformation", "lambda", "ec2", "s3"],
    "devops_tools": ["jenkins", "github", "gitlab", "circleci", "datadog", "grafana",
                     "prometheus", "splunk", "newrelic", "pagerduty", "jira"],
    "methodologies_practices": ["agile", "scrum", "kanban", "ci/cd", "devops", "tdd",
                                "microservices", "rest", "graphql", "oauth"],
    "data_ml": ["machine learning", "deep learning", "tensorflow", "pytorch", "pandas",
                "numpy", "spark", "hadoop", "kafka", "airflow", "dbt"],
}


class TermClusterer:
    """Clusters terms using word embeddings and k-means."""

    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_md")
        except OSError:
            print("Downloading spaCy model en_core_web_md...")
            spacy.cli.download("en_core_web_md")
            self.nlp = spacy.load("en_core_web_md")

    def get_embedding(self, term: str) -> Optional[np.ndarray]:
        """
        Get word embedding for a term.

        Returns None if term has no valid embedding.
        """
        doc = self.nlp(term)
        # Check if the vector is valid (not all zeros)
        if doc.vector.any():
            return doc.vector
        return None

    def find_optimal_k(self, embeddings: np.ndarray, max_k: int = 15) -> int:
        """
        Find optimal number of clusters using silhouette score.
        """
        n_samples = len(embeddings)
        if n_samples < 3:
            return 2

        max_k = min(max_k, n_samples - 1)
        if max_k < 2:
            return 2

        best_k = 2
        best_score = -1

        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)

            # Calculate silhouette score
            if len(set(labels)) > 1:  # Need at least 2 clusters
                score = silhouette_score(embeddings, labels)
                if score > best_score:
                    best_score = score
                    best_k = k

        return best_k

    def suggest_cluster_label(self, terms: list[str]) -> str:
        """
        Suggest a label for a cluster based on its terms.

        Uses anchor terms to identify known categories.
        """
        terms_lower = {t.lower() for t in terms}

        # Check overlap with anchor term categories
        best_category = None
        best_overlap = 0

        for category, anchors in ANCHOR_TERMS.items():
            overlap = len(terms_lower.intersection(set(anchors)))
            if overlap > best_overlap:
                best_overlap = overlap
                best_category = category

        if best_category and best_overlap >= 1:
            # Convert category key to readable label
            return best_category.replace("_", " ").title()

        # If no anchor match, use the most common/central term
        return f"Cluster ({terms[0]})"

    def cluster_terms(
        self,
        candidates: dict[str, CandidateTerm],
        num_clusters: Optional[int] = None
    ) -> ClusteringResult:
        """
        Cluster candidate terms using k-means on word embeddings.

        Args:
            candidates: Dictionary of filtered candidate terms
            num_clusters: Optional fixed number of clusters (auto-detect if None)

        Returns:
            ClusteringResult with clusters and metadata
        """
        # Get embeddings for all terms
        terms_with_embeddings = []
        embeddings = []
        unclusterable = []

        for key, candidate in candidates.items():
            term = candidate.term
            embedding = self.get_embedding(term)

            if embedding is not None:
                terms_with_embeddings.append(term)
                embeddings.append(embedding)
            else:
                unclusterable.append(term)

        if len(embeddings) < 2:
            return ClusteringResult(
                clusters=[],
                unclusterable=list(candidates.keys()),
                num_clusters=0,
                silhouette_score=0.0
            )

        embeddings_array = np.array(embeddings)

        # Determine optimal k if not specified
        if num_clusters is None:
            num_clusters = self.find_optimal_k(embeddings_array)

        # Run k-means
        kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(embeddings_array)

        # Calculate silhouette score
        if len(set(labels)) > 1:
            sil_score = silhouette_score(embeddings_array, labels)
        else:
            sil_score = 0.0

        # Group terms by cluster
        cluster_terms: dict[int, list[tuple[str, np.ndarray]]] = {}
        for term, embedding, label in zip(terms_with_embeddings, embeddings, labels):
            if label not in cluster_terms:
                cluster_terms[label] = []
            cluster_terms[label].append((term, embedding))

        # Build cluster objects
        clusters = []
        for cluster_id in sorted(cluster_terms.keys()):
            terms_and_embeddings = cluster_terms[cluster_id]
            terms = [t for t, _ in terms_and_embeddings]
            embs = np.array([e for _, e in terms_and_embeddings])

            # Find term closest to centroid
            centroid = kmeans.cluster_centers_[cluster_id]
            distances = np.linalg.norm(embs - centroid, axis=1)
            closest_idx = np.argmin(distances)
            centroid_nearest = terms[closest_idx]

            # Sort terms alphabetically for readability
            terms_sorted = sorted(terms, key=str.lower)

            cluster = Cluster(
                cluster_id=int(cluster_id),  # Convert numpy int to Python int
                terms=terms_sorted,
                suggested_label=self.suggest_cluster_label(terms),
                centroid_nearest=centroid_nearest
            )
            clusters.append(cluster)

        return ClusteringResult(
            clusters=clusters,
            unclusterable=unclusterable,
            num_clusters=num_clusters,
            silhouette_score=round(sil_score, 4)
        )
